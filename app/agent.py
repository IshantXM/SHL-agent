from typing import List, Dict, Any
from app.controller import handle_chat

def handle(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Orchestrate conversational recommendations.
    Delegates the flow decision logic to the new Controller.
    """
    return handle_chat(messages)