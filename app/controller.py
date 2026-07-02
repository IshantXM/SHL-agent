from typing import List, Dict, Any
import json
from app.config import CATALOG_PATH
from app.intent import detect_intent
from app.retriever import search
from app.guardrails import should_refuse, get_refusal_response
from app.clarifier import needs_clarification, get_clarification_response
from app.comparison import compare_assessments

# Load valid catalog names and URLs
try:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog_data = json.load(f)
    catalog_names = {item.get("name") for item in catalog_data if item.get("name")}
    catalog_urls = {item.get("link") for item in catalog_data if item.get("link")}
except Exception:
    catalog_names = set()
    catalog_urls = set()

def handle_chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Decides and routes queries to clarify/recommend/refine/compare/refuse.
    """
    if not messages:
        return {
            "reply": "How can I help you with assessments today?",
            "recommendations": [],
            "end_of_conversation": False
        }
        
    # Get the latest user message
    last_message = messages[-1]["content"]
    
    # 1. Guardrails check (Off-topic & Prompt Injection)
    if should_refuse(last_message):
        return get_refusal_response()
        
    # 2. Detect Intent and Extract Entities (with multi-turn context carry-over)
    combined_user_content = " ".join(
        msg["content"] for msg in messages if msg["role"] == "user"
    )
    
    intent_res = detect_intent(last_message)
    intent_type = intent_res.intent
    
    entities_res = detect_intent(combined_user_content)
    parsed_entities = {
        "role": entities_res.role,
        "skills": entities_res.skills,
        "experience": entities_res.experience
    }
    
    # 3. Router
    if intent_type == "refuse":
        return get_refusal_response()
        
    elif intent_type == "compare":
        return compare_assessments(last_message)
        
    elif intent_type == "clarify":
        return get_clarification_response(last_message, parsed_entities)
        
    elif intent_type in ["recommend", "refine"]:
        # Check if the query is vague/missing info, needing clarification
        if needs_clarification(last_message, parsed_entities):
            return get_clarification_response(last_message, parsed_entities)
            
        # Combine user messages for search context
        context = " ".join(
            msg["content"]
            for msg in messages
            if msg["role"] == "user"
        )
        
        # Search the catalog
        results = search(context, k=5)
        
        recommendations = []
        for item in results:
            recommendations.append({
                "name": item.get("name", ""),
                "url": item.get("link", item.get("url", "")),
                "test_type": "recommend"
            })
            
        # Filter recommendations to ensure name is in catalog_names and url is in catalog_urls
        filtered_recs = [
            r for r in recommendations 
            if r["name"] in catalog_names and r["url"] in catalog_urls
        ]
            
        return {
            "reply": f"Found {len(filtered_recs)} matching assessments.",
            "recommendations": filtered_recs,
            "end_of_conversation": False
        }
        
    # Default fallback
    return {
        "reply": "Unable to process request.",
        "recommendations": [],
        "end_of_conversation": False
    }
