from typing import List, Dict, Any
import json
import requests
from app.config import CATALOG_PATH, GEMINI_API_KEY
from app.intent import detect_intent
from app.parser import extract_assessment_preferences
from app.retriever import search
from app.guardrails import should_refuse, get_refusal_response
from app.clarifier import needs_clarification, get_clarification_response
from app.comparison import compare_assessments, sanitize_reply

# Load valid catalog names and URLs
try:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog_data = json.load(f)
    catalog_names = {item.get("name") for item in catalog_data if item.get("name")}
    catalog_urls = {item.get("link") for item in catalog_data if item.get("link")}
except Exception:
    catalog_names = set()
    catalog_urls = set()

def get_assessment_category(item: dict) -> str:
    name_lower = item.get("name", "").lower()
    keys_lower = [k.lower() for k in item.get("keys", [])]
    
    if "coding" in name_lower or "programming" in name_lower or "python" in name_lower or "java" in name_lower or "c++" in name_lower or "knowledge & skills" in keys_lower:
        return "coding"
    if "ability & aptitude" in keys_lower or "cognitive" in name_lower or "gsa" in name_lower or "aptitude" in name_lower:
        return "cognitive"
    if "personality & behavior" in keys_lower or "biodata & situational judgment" in keys_lower or "opq" in name_lower or "personality" in name_lower:
        return "personality"
    if "assessment exercises" in keys_lower or "simulation" in name_lower or "exercise" in name_lower:
        return "simulation"
    if "video interviews" in keys_lower or "structured interviews" in keys_lower or "interview" in name_lower:
        return "interview"
    return "other"

def generate_static_reply(parsed_entities: dict, recommendations: list, is_refinement: bool, messages: list) -> str:
    """Fallback generator for conversational, grounded replies."""
    role = parsed_entities.get("role") or (", ".join(parsed_entities.get("skills", [])) if parsed_entities.get("skills") else "")
    exp = parsed_entities.get("experience")
    assessment_pref = parsed_entities.get("assessment_pref", [])
    
    # Build natural fragments
    role_str = role if role else "your target role"
    exp_part = f"approximately {exp} years of experience" if exp else "your experience level"
    
    # Build preference description
    pref_map = {
        "coding": "coding and programming",
        "personality": "personality and behavioral",
        "cognitive": "cognitive and reasoning"
    }
    pref_labels = [pref_map.get(p, p) for p in assessment_pref]
    pref_str = " and ".join(pref_labels) if pref_labels else ""
    
    count = len(recommendations)
    
    if is_refinement:
        if pref_str:
            return (f"Got it. I've refined the shortlist to focus on {pref_str} assessments, "
                    f"tailored for a {role_str} role with {exp_part}. "
                    f"Here are {count} updated recommendations.")
        return (f"Based on your updated preferences, here are {count} refined SHL assessments "
              f"suitable for a {role_str} with {exp_part}.")
    else:
        if pref_str:
            return (f"Got it. Based on your preference for {pref_str} assessments and {exp_part}, "
                    f"here are {count} SHL assessments suitable for evaluating {role_str} skills.")
        return (f"Based on your requirements for a {role_str} with {exp_part}, "
                f"here are {count} SHL assessments I'd recommend.")

def llm_generate_reply(messages: List[Dict[str, str]], parsed_entities: dict, recommendations: list, is_refinement: bool) -> str:
    """Call Google Gemini API to write a dynamic conversational introduction reply."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    role = parsed_entities.get("role") or (", ".join(parsed_entities.get("skills", [])) if parsed_entities.get("skills") else "")
    exp = parsed_entities.get("experience")
    
    # Derive assessment preference labels from parsed_entities
    assessment_pref = parsed_entities.get("assessment_pref", [])
    pref_map = {
        "coding": "coding and programming",
        "personality": "personality and behavioral",
        "cognitive": "cognitive and reasoning"
    }
    pref_labels = [pref_map.get(p, p) for p in assessment_pref]
    pref_str = " and ".join(pref_labels) if pref_labels else "general"
    
    prompt = f"""You are an SHL Assessment Recommendation Assistant helping HR professionals find the right assessments.

Context:
- Target Role/Domain: {role or 'not specified'}
- Seniority/Experience: {exp or 'not specified'} years
- Assessment Preference: {pref_str}
- Number of assessments selected: {len(recommendations)}
- Assessment names: {[r['name'] for r in recommendations]}
- Is this a refinement of previous results: {is_refinement}

Recent conversation:
{json.dumps(messages[-4:] if len(messages) >= 4 else messages, indent=2)}

Write a brief, natural 1-2 sentence introduction to present these assessment recommendations.

Rules:
- Be conversational and warm (e.g. "Got it.", "Great.", "Based on your preferences...")
- Reference the user's specific role, experience level, and assessment type preference naturally
- If this is a refinement, acknowledge the update (e.g. "I've refined the shortlist...")
- Do NOT list the assessment names in the introduction
- Do NOT use markdown, bullet points, or numbered lists
- Keep it professional but human — like a helpful consultant, not a template
- End with a natural lead-in to the list (e.g. "here are five SHL assessments..." or "I'd recommend these assessments...")
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return sanitize_reply(raw)

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
    assessment_pref = extract_assessment_preferences(combined_user_content)
    parsed_entities = {
        "role": entities_res.role,
        "skills": entities_res.skills,
        "experience": entities_res.experience,
        "assessment_pref": assessment_pref
    }
    
    # 3. Router
    if intent_type == "refuse":
        return get_refusal_response()
        
    elif intent_type == "compare":
        return compare_assessments(last_message)
        
    elif intent_type == "clarify":
        # Even though the last message is short/vague, check if the accumulated
        # state from conversation history has enough info to recommend
        if needs_clarification(last_message, parsed_entities):
            return get_clarification_response(last_message, parsed_entities)
        # All info present from history — treat as a recommend
        intent_type = "recommend"
        
    if intent_type in ["recommend", "refine"]:
        # Check if the query is vague/missing info, needing clarification
        if needs_clarification(last_message, parsed_entities):
            return get_clarification_response(last_message, parsed_entities)
            
        # Combine user messages for search context
        context = " ".join(
            msg["content"]
            for msg in messages
            if msg["role"] == "user"
        )
        
        # Search the catalog (retrieve 15 candidates to allow category-based diversification)
        results = search(context, k=15)
        
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
        
        # Diversify recommendations (ensure unique categories first, then top remaining up to 5)
        seen_categories = set()
        final_recs = []
        
        # 1. Add unique categories first
        for r in filtered_recs:
            orig_item = next((item for item in catalog_data if item.get("name") == r["name"]), None)
            category = get_assessment_category(orig_item) if orig_item else "other"
            if category not in seen_categories:
                final_recs.append(r)
                seen_categories.add(category)
            if len(final_recs) == 5:
                break
                
        # 2. Fill to 5 with remaining items if unique count is less than 5
        if len(final_recs) < 5:
            for r in filtered_recs:
                if r not in final_recs:
                    final_recs.append(r)
                if len(final_recs) == 5:
                    break
        
        # 4. Generate conversational intro
        is_refinement = (intent_type == "refine")
        try:
            reply = llm_generate_reply(messages, parsed_entities, final_recs, is_refinement)
        except Exception:
            reply = generate_static_reply(parsed_entities, final_recs, is_refinement, messages)
            
        # Final output validation to guarantee only valid catalog names are returned
        valid_recs = [
            r for r in final_recs
            if r["name"] in catalog_names and 
            r["url"] in catalog_urls
        ]
        
        return {
            "reply": reply,
            "recommendations": valid_recs,
            "end_of_conversation": False
        }
        
    # Default fallback
    return {
        "reply": "Unable to process request.",
        "recommendations": [],
        "end_of_conversation": False
    }
