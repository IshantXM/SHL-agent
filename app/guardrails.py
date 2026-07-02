import re

# Specific keywords categorized by refusal reasons
REJECTION_KEYWORDS = {
    "legal_advice": [
        "law", "legal", "compliance", "sue", "suing", "court", "contract", 
        "labor standard", "employment law", "regulation", "fair labor", "eeoc"
    ],
    "salary_advice": [
        "salary", "pay", "compensation", "wage", "income", "money", 
        "remuneration", "package", "offer rate", "market rate", "pay scale"
    ],
    "general_hiring_advice": [
        "how to hire", "hiring process", "interview strategy", "onboard", 
        "onboarding", "retain", "retention", "recruit talent", "headcount", 
        "workplace culture", "how to write a job description"
    ],
    "non_shl_requests": [
        "hackerrank", "leetcode", "codility", "testdome", "codewars", 
        "weather", "movie", "politics", "sports", "cricket", "football", 
        "recipe", "song", "joke", "history", "news", "music"
    ]
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:previous|all|the)?\s*instructions",
    r"forget\s+(?:previous|all|the)?\s*instructions",
    r"you\s+are\s+now\s+(?:a|an)",
    r"act\s+as\s+(?:a|an)",
    r"system\s*prompt",
    r"reveal\s+your\s+instructions",
    r"bypass\s+(?:the|all)?\s*rules",
    r"override\s+(?:previous|all|the)?\s*instructions",
    r"jailbreak",
    r"ignore\s+everything\s+above",
]

def is_prompt_injection(query: str) -> bool:
    """Check if the query contains a potential prompt injection/override attack."""
    text = query.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def is_in_scope(query: str) -> bool:
    """
    Check if the query is in-scope for SHL assessment recommendations/comparisons.
    Returns False if it is related to legal, salary, general hiring advice, or non-SHL topics.
    """
    text = query.lower()
    
    # Check each category of out-of-scope keywords
    for category, keywords in REJECTION_KEYWORDS.items():
        if any(word in text for word in keywords):
            return False
            
    return True

def should_refuse(query: str) -> bool:
    """
    Return True if the query should be refused.
    Refuse if it is prompt injection OR if it is out of scope.
    """
    return is_prompt_injection(query) or not is_in_scope(query)

def get_refusal_response() -> dict:
    """Get the standard refusal response dictionary."""
    return {
        "reply": "I can only discuss SHL assessments. I cannot provide legal advice, salary information, general hiring advice, or answer non-SHL related questions.",
        "recommendations": [],
        "end_of_conversation": True
    }
