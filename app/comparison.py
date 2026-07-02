import json
from typing import List, Dict, Any
from app.config import CATALOG_PATH
from app.retriever import Retriever

# Load catalog for details
try:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
except Exception:
    catalog = []

def compare_assessments(query: str) -> dict:
    """
    Compare assessments mentioned or retrieved for the query.
    Generates a structured markdown table comparing their features.
    """
    # 1. Retrieve the top 3 candidates relevant to the query
    retriever = Retriever(k=3)
    candidates = retriever.get_results(query)
    
    if len(candidates) < 2:
        # If we got fewer than 2 from semantic search, let's try to find more items in catalog
        # by checking if keywords match
        query_words = [w.lower() for w in query.split() if len(w) > 2]
        extra_candidates = []
        for item in catalog:
            if item in candidates:
                continue
            name_lower = item.get("name", "").lower()
            if any(word in name_lower for word in query_words):
                extra_candidates.append(item)
                if len(candidates) + len(extra_candidates) >= 3:
                    break
        candidates.extend(extra_candidates)

    if not candidates:
        return {
            "reply": "I couldn't find any assessments matching your query to compare.",
            "recommendations": [],
            "end_of_conversation": False
        }
        
    if len(candidates) == 1:
        # Compare with similar items in catalog or just present the one
        # Let's find one more related item to compare against
        single_item = candidates[0]
        extra_candidates = [item for item in catalog if item.get("entity_id") != single_item.get("entity_id")][:1]
        candidates.extend(extra_candidates)

    # 2. Build comparison details
    reply_parts = []
    reply_parts.append(f"Here is a comparison of the relevant assessments I found for your request:\n")
    
    # Markdown Table Headers
    header = "| Feature | " + " | ".join(c.get("name", "Unknown") for c in candidates) + " |"
    divider = "| :--- | " + " | ".join(":---" for _ in candidates) + " |"
    reply_parts.append(header)
    reply_parts.append(divider)
    
    # Compare Job Levels
    job_levels_row = "| **Job Levels** | " + " | ".join(
        ", ".join(c.get("job_levels", [])) or "Not Specified" for c in candidates
    ) + " |"
    reply_parts.append(job_levels_row)
    
    # Compare Duration
    duration_row = "| **Duration** | " + " | ".join(
        c.get("duration") or "Not Specified" for c in candidates
    ) + " |"
    reply_parts.append(duration_row)
    
    # Compare Adaptive
    adaptive_row = "| **Adaptive** | " + " | ".join(
        ("Yes" if c.get("adaptive") == "yes" else "No") for c in candidates
    ) + " |"
    reply_parts.append(adaptive_row)
    
    # Compare Focus Keys
    keys_row = "| **Key Focus Areas** | " + " | ".join(
        ", ".join(c.get("keys", [])) or "Not Specified" for c in candidates
    ) + " |"
    reply_parts.append(keys_row)
    
    # Compare Description
    # Truncate description to first 150 chars or first sentence for compactness
    short_descriptions = []
    for c in candidates:
        desc = c.get("description", "No description available.")
        # Try to take the first sentence
        first_sentence = desc.split(". ")[0]
        if not first_sentence.endswith("."):
            first_sentence += "."
        if len(first_sentence) > 150:
            first_sentence = first_sentence[:147] + "..."
        short_descriptions.append(first_sentence)
        
    description_row = "| **Description** | " + " | ".join(short_descriptions) + " |"
    reply_parts.append(description_row)
    
    # 3. Format response recommendations list
    recommendations = []
    for c in candidates:
        recommendations.append({
            "name": c.get("name", ""),
            "url": c.get("link", c.get("url", "")),
            "test_type": "compare"
        })
        
    return {
        "reply": "\n".join(reply_parts),
        "recommendations": recommendations,
        "end_of_conversation": False
    }
