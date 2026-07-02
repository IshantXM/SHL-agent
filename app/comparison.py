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

def sanitize_reply(text: str) -> str:
    """Strip markdown artifacts (tables, bold, bullets, code fences) from LLM output."""
    # Remove code fences
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove markdown table pipes and dividers
    text = re.sub(r'\|+', '', text)
    # Remove markdown bold/italic asterisks
    text = re.sub(r'\*+', '', text)
    # Remove markdown heading markers
    text = re.sub(r'#+\s*', '', text)
    # Remove markdown bullet markers
    text = re.sub(r'^\s*[-•]\s+', '', text, flags=re.MULTILINE)
    # Remove markdown numbered list markers
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Collapse multiple newlines into single spaces for a paragraph feel
    text = re.sub(r'\n{2,}', '\n\n', text)
    # Collapse remaining single newlines into spaces (for table row remnants)
    text = re.sub(r'\s*\n\s*', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def llm_compare(assessment_a: dict, assessment_b: dict) -> str:
    """
    Call Google Gemini API to generate a conversational plain-text comparison.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""Compare the following two SHL assessments.

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

Instructions:
- Compare ONLY using catalog information.
- Explain: Purpose, Skills measured, Target roles, and Duration.
- Do not speculate.
- Do not provide hiring advice.
- Do not mention using assessments together unless explicitly stated in the catalog.
- Respond in plain text only.
- Do NOT use markdown symbols, bullet points, asterisks, tables, or pipe characters.
- Maximum 120 words total.
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
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    return sanitize_reply(raw)

def generate_static_comparison(candidates: List[dict]) -> str:
    """Fallback generator for plain-text comparison within 120 words."""
    if len(candidates) < 2:
        return "I couldn't find enough assessments to compare."
    
    a, b = candidates[0], candidates[1]
    
    a_name = a.get("name", "Assessment A")
    b_name = b.get("name", "Assessment B")
    
    a_keys = ", ".join(a.get("keys", [])) or "general assessment"
    b_keys = ", ".join(b.get("keys", [])) or "general assessment"
    
    a_duration = a.get("duration") or "unspecified duration"
    b_duration = b.get("duration") or "unspecified duration"
    
    a_levels = ", ".join(a.get("job_levels", [])) or "various levels"
    b_levels = ", ".join(b.get("job_levels", [])) or "various levels"
    
    a_desc = a.get("description", "")
    b_desc = b.get("description", "")
    
    a_summary = a_desc.split(". ")[0] + "." if a_desc else "No description available."
    b_summary = b_desc.split(". ")[0] + "." if b_desc else "No description available."
    
    reply = (
        f"{a_name} and {b_name} serve different purposes. "
        f"{a_name} focuses on {a_keys} for {a_levels} roles with a duration of {a_duration}, "
        f"assessing {a_summary} "
        f"{b_name} focuses on {b_keys} for {b_levels} roles with a duration of {b_duration}, "
        f"assessing {b_summary}"
    )
    
    # Trim to 120 words if needed
    words = reply.split()
    if len(words) > 120:
        reply = " ".join(words[:119]) + "."
        
    return reply

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
        # Fallback to static plain-text comparison
        reply_text = generate_static_comparison([assessment_a, assessment_b])
        
    return {
        "reply": reply_text,
        "recommendations": [],
        "end_of_conversation": False
    }
