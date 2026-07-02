import re
from dataclasses import dataclass

@dataclass
class IntentResult:
    intent: str
    role: str | None = None
    experience: int | None = None


def extract_role(text):
    """Extract job role from text"""
    roles = ["developer", "engineer", "manager", "analyst", "architect", "designer", "tester", "qa"]
    for role in roles:
        if role in text:
            return role
    return None


def extract_experience(text):
    """Extract years of experience from text"""
    match = re.search(r'(\d+)\s*(?:years?|y(?:\s|$))', text)
    if match:
        return int(match.group(1))
    return None


def detect_intent(text):
    """Detect user intent from text"""
    text_lower = text.lower()

    COMPARE_WORDS = ["difference", "compare", "versus", "vs", "better than"]
    if any(word in text_lower for word in COMPARE_WORDS):
        intent = "compare"
    elif any(word in text_lower for word in ["actually", "instead", "also", "include", "add"]):
        intent = "refine"
    else:
        intent = "recommend"

    role = extract_role(text_lower)
    experience = extract_experience(text_lower)

    return IntentResult(
        intent=intent,
        role=role,
        experience=experience
    )


# Test
if __name__ == "__main__":
    test_queries = [
        "Hiring Java developer 4 years",
        "Looking for a Python engineer with 5 years experience",
        "What's the difference between analyst and designer?",
        "Actually I need a QA manager",
    ]

    print("="*60)
    print("INTENT DETECTION WITH STRUCTURED OUTPUT")
    print("="*60)

    for query in test_queries:
        result = detect_intent(query)
        print(f"\nQuery: {query}")
        print(f"Result: IntentResult(")
        print(f"   intent=\"{result.intent}\",")
        print(f"   role=\"{result.role}\",")
        print(f"   experience={result.experience}")
        print(f")")

    print("\n" + "="*60)
