import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.schemas import ChatRequest, ChatResponse, Recommendation
from app.intent import detect_intent
from app.retriever import search


def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process chat request and generate recommendations.
    """

    # Get latest user message
    user_message = next(
        (
            msg.content
            for msg in reversed(request.messages)
            if msg.role == "user"
        ),
        None
    )

    if user_message is None:
        return ChatResponse(
            reply="No user message found.",
            recommendations=[],
            end_of_conversation=True
        )

    # Detect intent
    intent = detect_intent(user_message)

    # Retrieve results
    products = search(user_message, k=3)

    # Build recommendations
    recommendations = []

    for product in products:
        recommendations.append(
            Recommendation(
                name=product.get("name", "Unknown"),
                url=product.get("link", ""),
                test_type=intent
            )
        )

    replies = {
        "compare":
            f"I found products to compare for '{user_message}'.",

        "refine":
            f"I refined the search for '{user_message}'.",

        "recommend":
            f"I found {len(recommendations)} recommendations.",

        "clarify":
            f"Could you provide more details about '{user_message}'?",

        "refuse":
            "I can only help with product recommendations."
    }

    reply = replies.get(
        intent,
        f"Results for '{user_message}'."
    )

    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=False
    )


if __name__ == "__main__":

    json_request = """
    {
        "messages": [
            {
                "role": "user",
                "content": "Hiring Java developer with 4 years experience"
            }
        ]
    }
    """

    print("Input JSON")
    print("-" * 60)
    print(json_request)

    data = json.loads(json_request)

    request = ChatRequest(**data)

    response = process_chat(request)

    print("\nResponse JSON")
    print("-" * 60)

    print(
        json.dumps(
            response.model_dump(),
            indent=2
        )
    )