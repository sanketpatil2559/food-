"""
RAG Engine - The Brain of Our Food Chatbot
==========================================
RAG = Retrieval Augmented Generation

Simple explanation:
  1. We have a food database (our "knowledge")
  2. When user asks something, we SEARCH the database for relevant food items
  3. We send those relevant items + the user's question to Claude AI
  4. Claude gives a smart answer based on real data (not just guessing)

This file handles Step 1 and Step 2 (the "Retrieval" part of RAG).
"""

import json
import os
import re
from pathlib import Path


def load_food_data() -> list[dict]:
    """Load all food items from our JSON knowledge base."""
    data_path = Path(__file__).parent / "food_knowledge.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def simple_search(query: str, foods: list[dict], top_k: int = 4) -> list[dict]:
    """
    Simple keyword-based search (no fancy ML needed!).
    
    We score each food item based on how many query words match
    its title, tags, mood, cuisine, ingredients, etc.
    
    This is our "Retrieval" step in RAG.
    """
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    # Words we ignore (too common, not useful for search)
    stop_words = {
        'i', 'want', 'me', 'give', 'a', 'an', 'the', 'is', 'are',
        'some', 'food', 'eat', 'suggest', 'recommend', 'please', 'can',
        'you', 'what', 'should', 'something', 'anything', 'like', 'have',
        'for', 'to', 'and', 'or', 'with', 'in', 'of', 'my', 'do'
    }
    keywords = query_words - stop_words

    scored_foods = []
    for food in foods:
        score = 0
        
        # Build a big string of everything about this food
        searchable_text = " ".join([
            food["title"].lower(),
            food["cuisine"].lower(),
            food["category"].lower(),
            food["description"].lower(),
            " ".join(food.get("tags", [])),
            " ".join(food.get("mood", [])),
            " ".join(food.get("ingredients", [])),
            " ".join(food.get("best_for", [])),
            food.get("region", "").lower(),
            "vegetarian" if food.get("veg") else "non-vegetarian chicken meat fish",
        ])

        # Score based on keyword matches
        for keyword in keywords:
            if keyword in searchable_text:
                score += 1
                # Bonus: keyword in title = more relevant
                if keyword in food["title"].lower():
                    score += 2

        # Special intent detection
        if any(w in query_lower for w in ["veg", "vegetarian", "no meat", "plant"]):
            if food.get("veg"):
                score += 3
        
        if any(w in query_lower for w in ["non veg", "nonveg", "chicken", "fish", "meat", "egg"]):
            if not food.get("veg"):
                score += 3

        if any(w in query_lower for w in ["breakfast", "morning", "light"]):
            if "breakfast" in food.get("best_for", []):
                score += 2

        if any(w in query_lower for w in ["dessert", "sweet", "mithai"]):
            if food.get("category") == "Dessert":
                score += 4

        if any(w in query_lower for w in ["quick", "fast", "easy"]):
            if food.get("difficulty") == "Easy":
                score += 2

        if score > 0:
            scored_foods.append((score, food))

    # Sort by score, return top results
    scored_foods.sort(key=lambda x: x[0], reverse=True)
    
    # If nothing matched, return a random sample so we always have context
    if not scored_foods:
        return foods[:top_k]
    
    return [food for _, food in scored_foods[:top_k]]


def build_context(relevant_foods: list[dict]) -> str:
    """
    Convert our food items into a readable text block.
    This text block gets sent to Claude as "context" (the RAG part).
    """
    if not relevant_foods:
        return "No specific food items found."

    context_lines = ["Here are relevant food items from our database:\n"]
    
    for food in relevant_foods:
        veg_label = "🟢 Vegetarian" if food.get("veg") else "🔴 Non-Vegetarian"
        context_lines.append(f"""
--- {food['title']} ---
Cuisine: {food['cuisine']} | Category: {food['category']} | {veg_label}
Region: {food.get('region', 'Pan India')}
Description: {food['description']}
Main Ingredients: {', '.join(food.get('ingredients', []))}
Best For: {', '.join(food.get('best_for', []))}
Pairs Well With: {', '.join(food.get('pairs_with', []))}
Calories: ~{food.get('calories_per_serving', 'N/A')} per serving
Prep Time: {food.get('prep_time', 'N/A')}
Difficulty: {food.get('difficulty', 'N/A')}
Mood Tags: {', '.join(food.get('mood', []))}
""")

    return "\n".join(context_lines)


def retrieve_context(user_query: str) -> str:
    """
    Main function: Given a user query, find relevant foods and return context.
    This is the "R" in RAG (Retrieval).
    """
    all_foods = load_food_data()
    relevant_foods = simple_search(user_query, all_foods, top_k=4)
    context = build_context(relevant_foods)
    return context


def get_system_prompt(context: str) -> str:
    """
    Build the system prompt that tells Claude how to behave.
    We inject our retrieved food context here.
    """
    return f"""You are FoodieBot 🍛, a friendly and knowledgeable Indian food recommendation assistant.

You help users discover the perfect meal based on their mood, hunger level, dietary preferences, time of day, and taste preferences.

IMPORTANT RULES:
1. ONLY recommend foods from the provided database context below
2. Be warm, enthusiastic and conversational — like a foodie friend!
3. Always explain WHY you're recommending a dish
4. Mention key details: ingredients, pairings, calories if relevant
5. If user asks for vegetarian options, only suggest veg items
6. Use food emojis to make responses fun 🍽️
7. If the user's query doesn't match any food well, politely say so and ask clarifying questions
8. Keep responses concise but informative (2-4 paragraphs max)

--- FOOD DATABASE CONTEXT ---
{context}
--- END OF CONTEXT ---

Based ONLY on the foods in the context above, give personalized, helpful recommendations.
Do not make up foods that are not in the context.
"""
