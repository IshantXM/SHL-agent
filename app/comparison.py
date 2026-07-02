import json
import re
import requests
from typing import List, Dict, Any
from app.config import CATALOG_PATH, GEMINI_API_KEY
from app.retriever import Retriever

# Load catalog for details
try:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
except Exception:
    catalog = []

def get_catalog(item_name_or_query: str) -> dict | None:
    """Helper to fetch a single matching catalog item using semantic search."""
    if not item_name_or_query:
        return None
    retriever = Retriever(k=1)
    results = retriever.get_results(item_name_or_query)
    return results[0] if results else None

def llm_compare(assessment_a: dict, assessment_b: dict) -> str:
    """
    Call Google Gemini API to generate a side-by-side comparison table.
    Falls back to generating a static table on failure.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
Compare the following two SHL assessments ONLY using the supplied catalog data. Do not invent any facts.

Assessment A:
Name: {assessment_a.get('name')}
Job Levels: {assessment_a.get('job_levels')}
Duration: {assessment_a.get('duration')}
Adaptive: {assessment_a.get('adaptive')}
Keys/Categories: {assessment_a.get('keys')}
Description: {assessment_a.get('description')}

Assessment B:
Name: {assessment_b.get('name')}
Job Levels: {assessment_b.get('job_levels')}
Duration: {assessment_b.get('duration')}
Adaptive: {assessment_b.get('adaptive')}
Keys/Categories: {assessment_b.get('keys')}
Description: {assessment_b.get('description')}

Please provide a side-by-side comparison table in markdown with columns "Feature", "{assessment_a.get('name')}", "{assessment_b.get('name')}".
Compare these features:
- Purpose
- Skills measured
- Target roles
- Duration
- Use cases

Do not include any introductory conversation.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def generate_static_comparison(candidates: List[dict]) -> str:
    """Fallback generator for static comparison table."""
    reply_parts = []
    reply_parts.append(f"Here is a comparison of the relevant assessments I found for your request:\n")
    
    header = "| Feature | " + " | ".join(c.get("name", "Unknown") for c in candidates) + " |"
    divider = "| :--- | " + " | ".join(":---" for _ in candidates) + " |"
    reply_parts.append(header)
    reply_parts.append(divider)
    
    job_levels_row = "| **Job Levels** | " + " | ".join(", ".join(c.get("job_levels", [])) or "Not Specified" for c in candidates) + " |"
    reply_parts.append(job_levels_row)
    
    duration_row = "| **Duration** | " + " | ".join(c.get("duration") or "Not Specified" for c in candidates) + " |"
    reply_parts.append(duration_row)
    
    adaptive_row = "| **Adaptive** | " + " | ".join(("Yes" if c.get("adaptive") == "yes" else "No") for c in candidates) + " |"
    reply_parts.append(adaptive_row)
    
    keys_row = "| **Key Focus Areas** | " + " | ".join(", ".join(c.get("keys", [])) or "Not Specified" for c in candidates) + " |"
    reply_parts.append(keys_row)
    
    short_descriptions = []
    for c in candidates:
        desc = c.get("description", "No description available.")
        first_sentence = desc.split(". ")[0]
        if not first_sentence.endswith("."):
            first_sentence += "."
        if len(first_sentence) > 150:
            first_sentence = first_sentence[:147] + "..."
        short_descriptions.append(first_sentence)
        
    description_row = "| **Description** | " + " | ".join(short_descriptions) + " |"
    reply_parts.append(description_row)
    
    return "\n".join(reply_parts)

def compare_assessments(query: str) -> dict:
    """
    Compare assessments mentioned or retrieved for the query using either
    the dynamic LLM comparator or the static table fallback.
    """
    # 1. Parse two potential targets
    q = query.lower()
    for word in ["compare", "difference between", "difference", "versus", "comparison of", "comparison"]:
        q = q.replace(word, "")
        
    parts = []
    if "vs" in q:
        parts = [p.strip() for p in q.split("vs")]
    elif "and" in q:
        parts = [p.strip() for p in q.split("and")]
        
    assessment_a = None
    assessment_b = None
    
    if len(parts) >= 2:
        assessment_a = get_catalog(parts[0])
        assessment_b = get_catalog(parts[1])
        
    # 2. Fallback to semantic search for top 2 candidates if parsing failed
    if not assessment_a or not assessment_b:
        retriever = Retriever(k=2)
        candidates = retriever.get_results(query)
        if len(candidates) >= 2:
            assessment_a = candidates[0]
            assessment_b = candidates[1]
            
    if not assessment_a:
        return {
            "reply": "I couldn't find any assessments matching your query to compare.",
            "recommendations": [],
            "end_of_conversation": False
        }
        
    # If we only have one candidate, select a related one from the catalog to compare against
    if not assessment_b:
        assessment_b = [item for item in catalog if item.get("entity_id") != assessment_a.get("entity_id")][0]
        
    # 3. Perform comparison
    try:
        reply_text = llm_compare(assessment_a, assessment_b)
    except Exception:
        # Fallback to static table
        reply_text = generate_static_comparison([assessment_a, assessment_b])
        
    return {
        "reply": reply_text,
        "recommendations": [],
        "end_of_conversation": False
    }
