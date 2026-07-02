from fastapi import FastAPI, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.agent import handle


app = FastAPI(

    title="Assessment Recommendation API",

    description="""
SHL-style assessment recommendation service.

Features:
- Intent detection
- Query parsing
- Semantic retrieval
- Assessment recommendations
""",

    version="1.0.0"

)


@app.get("/")
def root():

    return {

        "service": "Assessment Recommendation API",

        "version": "1.0.0",

        "status": "running"

    }


@app.get("/health")
def health():

    return {

        "status": "ok"

    }


@app.post(

    "/chat",

    response_model=ChatResponse

)

def chat(

    request: ChatRequest

):

    try:

        messages = [

            {

                "role": m.role,

                "content": m.content

            }

            for m in request.messages

        ]

        response = handle(

            messages

        )

        return response

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )