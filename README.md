# 🍛 FoodieBot — AI Food Recommendation Chatbot with RAG

> A beginner-friendly project that teaches you how to build an AI chatbot using RAG (Retrieval Augmented Generation) and Groq AI.

---

## 📖 What Is This Project?

FoodieBot is a **chat app** where you talk to an AI and it recommends Indian food based on your mood, preferences, and cravings.

**What makes it special?** It uses a technique called **RAG** — instead of the AI just guessing, it first searches through a real food database, then gives answers based on actual data.

---

## 🤔 What is RAG? (Super Simple Explanation)

Imagine you're asking a friend "What should I eat tonight?"

**Without RAG:** Your friend just guesses from memory. Sometimes wrong, sometimes makes things up.

**With RAG:** Your friend first opens a cookbook, finds the relevant pages, THEN gives you a recommendation based on real recipes.

RAG = **R**etrieval **A**ugmented **G**eneration

```
User asks something
      ↓
[RETRIEVAL] Search our food database for relevant items
      ↓
[AUGMENTATION] Add those items as context to the AI's prompt
      ↓
[GENERATION] AI generates a smart answer based on real data
```

That's it! It's just: Search first → Then Answer.

---

## 📁 Project Structure

```
food-rag-chatbot/
│
├── main.py                 ← Web server that handles requests
├── rag_engine.py           ← RAG logic: search + retrieve context
├── index.html              ← The chat UI
├── food_knowledge.json     ← Our food database (12 dishes)
├── README.md               ← Project docs
└── __pycache__/            ← Python cache files
```

**Simple explanation of each file:**

| File | What it does | Think of it as |
|------|-------------|----------------|
| `food_knowledge.json` | Stores all food info | Our cookbook |
| `rag_engine.py` | Searches the cookbook | Our search engine |
| `main.py` | Handles web requests, calls Groq | The server waiter |
| `index.html` | The chat interface | The restaurant front desk |

---

## 🛠️ How to Set Up (Step by Step)

### Step 1 — Get a Groq API Key

1. Go to **https://console.groq.ai**
2. Sign up for a free account
3. Click "API Keys" → "Create Key"
4. Copy the key (it starts with `gsk_...`)
5. Save it somewhere safe!

### Step 2 — Install Python (if you don't have it)

1. Go to **https://python.org/downloads**
2. Download Python 3.11 or newer
3. Install it (check "Add Python to PATH" during install)
4. Verify by opening Terminal/Command Prompt and typing:
   ```
   python --version
   ```
   You should see something like `Python 3.11.5`

### Step 3 — Download/Clone This Project

If you have Git:
```bash
git clone <your-repo-url>
cd food-rag-chatbot
```

Or just download and extract the ZIP file.

### Step 4 — Set Up the Backend (Python Server)

Open Terminal/Command Prompt:

```bash
# From the project root
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

You should see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

✅ **Leave this terminal open!** The server needs to keep running.

### Step 5 — Open the Frontend (Chat UI)

1. Open the project folder on your computer
2. Double-click `index.html`
3. It opens in your web browser!

### Step 6 — Connect Your API Key

1. In the chat UI, find the "🔑 Your API Key" box on the left
2. Paste your Groq API key
3. Click **Connect**
4. The badge should turn green: "● Connected"

### Step 7 — Start Chatting! 🎉

Try typing:
- *"I want something vegetarian for dinner"*
- *"What's a good breakfast dish?"*
- *"I'm craving something sweet"*

---

## 🧠 How The Code Works (Step by Step)

When you send a message, here's what happens:

```
1. You type "I want something spicy and vegetarian"
         ↓
2. Frontend (index.html) sends this to Backend (main.py)
         ↓
3. rag_engine.py searches food_knowledge.json
   → Finds: Palak Paneer, Masala Dosa, Pav Bhaji...
         ↓
4. Builds a "context" text with details about those dishes
         ↓
5. Sends context + your question to Groq AI
   "Here are the relevant dishes: [Palak Paneer info...]
    User asks: I want something spicy and vegetarian"
         ↓
6. Groq reads the context and gives a personalized answer
         ↓
7. Answer appears in your chat window ✨
```

---

## 🔧 Customizing the Project

### Add More Food Items

Open `food_knowledge.json` and add a new item following this format:

```json
{
  "id": "13",
  "title": "Your Dish Name",
  "cuisine": "Indian",
  "category": "Vegetarian",
  "mood": ["light", "healthy"],
  "tags": ["keyword1", "keyword2"],
  "description": "Description of the dish...",
  "ingredients": ["ingredient1", "ingredient2"],
  "best_for": ["breakfast", "lunch"],
  "pairs_with": ["rice", "roti"],
  "calories_per_serving": 300,
  "prep_time": "30 minutes",
  "difficulty": "Easy",
  "region": "South India",
  "veg": true
}
```

### Change the AI's Personality

Open `rag_engine.py` and find the `get_system_prompt()` function. Edit the text there to change how FoodieBot talks.

### Change the Color Theme

Open `frontend/index.html` and find the `:root { }` section near the top. Change the color values like `--saffron: #F97316;` to any color you want.

---

## 🚨 Common Problems & Fixes

| Problem | What to check |
|---------|--------------|
| "Could not reach the server" | Make sure `uvicorn main:app --reload` is running |
| "Invalid API key" | Make sure key starts with `gsk_` |
| Blank page | Open browser console (F12) and check for errors |
| `pip not found` | Try `pip3 install -r requirements.txt` |
| Port already in use | Run `uvicorn main:app --reload --port 8001` |

---

## 📚 What You Learned

By building this project, you now understand:

- ✅ What **RAG** is and why it's useful
- ✅ How to build a **REST API** with FastAPI (Python)
- ✅ How to call the **Groq AI API**
- ✅ How to pass **context** to an LLM (Language Model)
- ✅ How a **frontend** communicates with a **backend**
- ✅ Basic **search/retrieval** without complex ML

---

## 🚀 Next Steps to Level Up

Once you're comfortable, try these upgrades:

1. **Better Search** — Replace keyword search with vector embeddings (ChromaDB or FAISS)
2. **More Food Data** — Add hundreds of dishes from a real dataset
3. **User Accounts** — Let users save their favorite dishes
4. **Recipe Steps** — Add full cooking instructions
5. **Image Support** — Show dish photos in the chat

---

## 📞 Need Help?

- Groq Docs: **https://docs.groq.ai**
- FastAPI Docs: **https://fastapi.tiangolo.com**

---

*Built with ❤️, Python, and a lot of hunger 🍛*
