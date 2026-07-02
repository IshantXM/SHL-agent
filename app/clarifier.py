def extract_test_types(text: str) -> list[str]:
    """Identify which test categories (cognitive, personality, coding) are in the query."""
    text_lower = text.lower()
    types = []
    if any(w in text_lower for w in ["cognitive", "aptitude", "ability", "reasoning", "logic"]):
        types.append("cognitive")
    if any(w in text_lower for w in ["personality", "behavior", "situational", "opq"]):
        types.append("personality")
    if any(w in text_lower for w in ["coding", "programming", "technical", "test code", "coding required"]):
        types.append("coding")
    return types

def needs_clarification(query: str, parsed_entities: dict) -> bool:
    """
    Determine if more information is required based on the clarification policy:
    We need clarification if role/skills, seniority/experience, or test type is missing.
    """
    role_present = bool(parsed_entities.get("role") or parsed_entities.get("skills"))
    experience = parsed_entities.get("experience")
    test_types = extract_test_types(query)
    
    # If any of the three (role/skills, seniority, or test type) is missing, clarify.
    if not role_present or not experience or not test_types:
        return True
        
    return False

def get_clarification_response(query: str, parsed_entities: dict) -> dict:
    """
    Generate dynamic clarification reply following the specific policy:
    1. If role/skills is missing -> Ask for job role.
    2. If role/skills is present but seniority is missing -> Ask for seniority.
    3. If role/skills & seniority are present but test type is missing -> Ask for assessment preferences.
    """
    role_present = bool(parsed_entities.get("role") or parsed_entities.get("skills"))
    experience = parsed_entities.get("experience")
    
    if not role_present:
        reply = "Could you specify the target job role (e.g. Java Developer) for the assessment?"
    elif not experience:
        reply = "What seniority level or years of experience is required for this role?"
    else:
        reply = "Would you prefer a Cognitive, Personality, or Coding assessment for this role?"
        
    return {
        "reply": reply,
        "recommendations": [],
        "end_of_conversation": False
    }
