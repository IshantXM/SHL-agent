def needs_clarification(query: str, parsed_entities: dict) -> bool:
    """
    Determine if more information is required based on the clarification policy:
    We need clarification if role/skills, seniority/experience, or assessment preference is missing.
    """
    role_present = bool(parsed_entities.get("role") or parsed_entities.get("skills"))
    experience = parsed_entities.get("experience")
    assessment_pref = parsed_entities.get("assessment_pref")
    
    # If any of the three (role/skills, seniority, or assessment preference) is missing, clarify.
    if not role_present or not experience or not assessment_pref:
        return True
        
    return False

def get_clarification_response(query: str, parsed_entities: dict) -> dict:
    """
    Generate dynamic clarification reply following the specific policy:
    1. If role/skills is missing -> Ask for job role.
    2. If role/skills is present but seniority is missing -> Ask for seniority.
    3. If role/skills & seniority are present but assessment preference is missing -> Ask for assessment preferences.
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
