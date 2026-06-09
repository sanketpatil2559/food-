"""
FastAPI Backend Server
======================
This is our web server. It:
  1. Receives chat messages from the frontend (React app)
  2. Runs the RAG engine to find relevant food context
  3. Sends the context + message to Claude AI
  4. Returns Claude's response back to the frontend

To run: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import ssl
import os
from rag_engine import retrieve_context, get_system_prompt

# ─── App Setup ────────────────────────────────────────────────
app = FastAPI(title="Food RAG Chatbot API", version="1.0.0")

# Allow our React frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data Models ─────────────────────────────────────────────
class Message(BaseModel):
    role: str          # "user" or "assistant"
    content: str       # the actual message text

class ChatRequest(BaseModel):
    messages: list[Message]          # full conversation history
    api_key: Optional[str] = None    # user's Groq API key

class ChatResponse(BaseModel):
    reply: str
    context_used: str          # for debugging: what food data was retrieved

# ─── Routes ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Flow:
    1. Get the latest user message
    2. Run RAG: search food database for relevant items
    3. Build system prompt with retrieved context
    4. Call Groq API with full conversation history
    5. Return the Groq model's reply
    """
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    api_key = request.api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    if not api_key.startswith("gsk_"):
        raise HTTPException(status_code=400, detail="That does not look like a valid Groq API key")

    # Step 1: Get the latest user message for RAG search
    last_user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            last_user_message = msg.content
            break

    # Step 2: RAG - Retrieve relevant food context
    food_context = retrieve_context(last_user_message)
    
    # Step 3: Build the system prompt with context
    system_prompt = get_system_prompt(food_context)
    
    # Step 4: Call Groq API using Chat Completions format
    # Build messages list: system prompt + conversation history
    groq_messages = [
        {"role": "system", "content": system_prompt}
    ]
    for msg in request.messages:
        groq_messages.append({"role": msg.role, "content": msg.content})

    groq_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": groq_messages,
        "max_tokens": 1024,
        "temperature": 0.2,
    }
    groq_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    async def call_groq(timeout_seconds: float):
        """Single attempt to call Groq with the given timeout."""
        async with httpx.AsyncClient(timeout=timeout_seconds, trust_env=True) as client:
            return await client.post(
                GROQ_URL,
                headers=groq_headers,
                json=groq_payload,
            )

    try:
        # First attempt — fast timeout (20s)
        try:
            response = await call_groq(20.0)
        except httpx.TimeoutException:
            # Retry once with a longer timeout before giving up
            try:
                response = await call_groq(45.0)
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Request to Groq API timed out after two attempts. Try again in a moment."
                )

        if response.status_code != 200:
            body = response.json()
            # Groq error format: {"error": {"message": "...", "type": "..."}}
            error_obj = body.get("error", {})
            if isinstance(error_obj, dict):
                error_detail = error_obj.get("message") or str(error_obj)
            else:
                error_detail = str(error_obj) or body.get("message") or "Unknown error"
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Groq API error: {error_detail}"
            )

        data = response.json()
        # Standard Chat Completions response: choices[0].message.content
        try:
            reply_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            reply_text = str(data)

        return ChatResponse(
            reply=reply_text,
            context_used=food_context
        )

    except HTTPException:
        raise  # re-raise our own HTTP exceptions unchanged

    except httpx.ConnectError as e:
        err_str = str(e).lower()
        if "ssl" in err_str or "certificate" in err_str:
            detail = (
                "SSL/TLS error connecting to Groq API. "
                "This can happen due to corporate firewalls or antivirus software intercepting HTTPS. "
                f"Details: {str(e)}"
            )
        elif "name" in err_str or "resolve" in err_str or "dns" in err_str:
            detail = (
                "DNS resolution failed — cannot reach api.groq.com. "
                "Check your internet connection or DNS settings. "
                f"Details: {str(e)}"
            )
        elif "refused" in err_str:
            detail = (
                "Connection refused by Groq API. "
                "The service may be temporarily unavailable. "
                f"Details: {str(e)}"
            )
        else:
            detail = (
                "Could not connect to Groq API. "
                "Check your network / internet connection. "
                f"Details: {str(e)}"
            )
        raise HTTPException(status_code=503, detail=detail)

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Network error while talking to Groq API. "
                "Check your internet connection and try again. "
                f"Error: {str(e)}"
            )
        )


@app.get("/foods")
def get_all_foods():
    """Return all foods in our database (useful for browsing)."""
    from rag_engine import load_food_data
    return load_food_data()


@app.get("/search")
def search_foods(query: str):
    """Test the RAG retrieval without calling Claude."""
    from rag_engine import load_food_data, simple_search
    all_foods = load_food_data()
    results = simple_search(query, all_foods)
    return {"query": query, "results": results}
