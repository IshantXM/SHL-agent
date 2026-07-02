import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from app.schemas import ChatRequest, ChatResponse, Message, Recommendation
from app.intent import detect_intent
from app.retriever import search

def process_chat(request: ChatRequest) -> ChatResponse:
    """Process chat request and return response"""
    
    # Get the last user message
    user_message = None
    for msg in request.messages:
        if msg.role == "user":
            user_message = msg.content
    
    if not user_message:
        return ChatResponse(
            reply="No user message found",
            recommendations=[],
            end_of_conversation=True
        )
    
    # Detect intent
    intent = detect_intent(user_message)
    
    # Search for recommendations
    products = search(user_message, k=3)
    
    # Build recommendations
    recommendations = [
        Recommendation(
            name=p['name'],
            url=p.get('link', '#'),
            test_type=intent
        )
        for p in products
    ]
    
    # Generate reply based on intent
    replies = {
        "compare": f"Here are comparison products for: {user_message}",
        "refine": f"Let me refine the search: {user_message}",
        "refuse": "I'm not sure I can help with that. Please ask about our products.",
        "clarify": f"Could you be more specific about: {user_message}?",
        "recommend": f"Based on your request, I found these recommendations:"
    }
    
    reply = replies.get(intent, f"Here are results for: {user_message}")
    
    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=False
    )


# Test with JSON
if __name__ == "__main__":
    # JSON request (as string)
    json_request = """
    {
      "messages": [
        {
          "role": "user",
          "content": "Hiring Java developer 4 years"
        }
      ]
    }
    """
    
    # Parse JSON to dict
    data = json.loads(json_request)
    
    # Convert to ChatRequest object
    request = ChatRequest(**data)
    
    # Process the request
    response = process_chat(request)
    
    # Print as JSON
    print("Response:")
    print(json.dumps(response.dict(), indent=2))
    
    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=False
    )


# Test
if __name__ == "__main__":
    # Example request
    request = ChatRequest(
        messages=[
            Message(role="user", content="Hiring Java developer 4 years")
        ]
    )
    
    response = process_chat(request)
    
    print(f"Reply: {response.reply}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(response.recommendations, 1):
        print(f"  {i}. {rec.name} ({rec.test_type})")
