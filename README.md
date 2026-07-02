# SHL Conversational Assessment Recommender

This project implements a conversational AI agent designed to help recruiters and hiring managers discover relevant SHL assessments through natural language dialogue. The system leverages semantic retrieval (FAISS), Intent Detection, and Google's Gemini API to guide users from vague hiring needs to precise assessment recommendations.

## Overview

The goal of this agent is to simplify the discovery of SHL's extensive catalog (377+ assessments). Instead of browsing manually, users can simply state their hiring needs (e.g., "I need a coding test for a senior Java developer") and the agent will intelligently clarify missing requirements, retrieve the best matches, or compare specific assessments.

## Architecture

```text
User Query
    ↓
Intent Detection
    ↓
Controller
    ↓
Clarification Policy
    ↓
Retriever
    ↓
FAISS
    ↓
Ranker
    ↓
Gemini (Comparison)
    ↓
Validation
    ↓
FastAPI
    ↓
JSON Response
```

## Features and Behaviors

The agent seamlessly supports four core behaviors:
1. **Clarification**: If a request is vague (missing role, seniority, or preference), the agent politely asks for the missing information.
2. **Recommendation**: Retrieves and recommends the top SHL assessments matching the user's specific role and experience requirements.
3. **Refinement**: Allows users to tweak their requirements (e.g., "Actually, add personality tests too") and updates the recommendations.
4. **Comparison**: Uses the Gemini API to compare two assessments side-by-side using strictly catalog data (no hallucinations or external advice).

**Guardrails**: The agent strictly operates within the SHL domain. It actively detects and refuses prompt injections, legal questions, salary advice, and requests for external non-SHL certifications (e.g., AWS/Azure exams, Coursera courses).

## Installation

```bash
# Clone the repository
git clone <repository_url>
cd <repository_directory>

# Install dependencies
pip install -r requirements.txt
```

## Running Locally

Start the FastAPI application with Uvicorn:

```bash
python -m uvicorn app.main:app --reload
```
or
```bash
uvicorn app.main:app --reload
```

## Docker

Build the image:
```bash
docker build -t shl-agent .
```

Run the container:
```bash
docker run -p 8000:8000 shl-agent
```

Check the health status:
```text
http://localhost:8000/health
```

## Endpoints

- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
  - Expected: `{"status": "ok"}`
- **Chat Endpoint**: `POST http://localhost:8000/chat`
  - Body Example:
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "Hiring Java developer"
        }
      ]
    }
    ```

## Evaluation and Metrics

The system includes a comprehensive evaluation suite measuring intent accuracy, retrieval recall, groundedness, and safeguard compliance.

Run the behavior/unit tests:
```bash
python tests/test_agent_system.py
```

Run the evaluation suite:
```bash
python app/evaluation.py
```

**System Metrics:**
- **Intent Detection Accuracy**: 100%
- **Guardrail F1**: 100%
- **Clarification Pass Rate**: 100%
- **Refinement Pass Rate**: 100%
- **Comparison Pass Rate**: 100%
- **Recall@10**: 61.11%
- **Groundedness**: 92.17%
- **Hallucination Rate**: 8.70%

## Project Structure

- `app/main.py`: FastAPI application entry point.
- `app/agent.py` & `app/controller.py`: Core routing and conversational logic.
- `app/retriever.py`: FAISS-based semantic search.
- `app/clarifier.py`: State tracking and clarification rules.
- `app/guardrails.py`: Scope control and prompt injection protection.
- `app/comparison.py`: Gemini-powered side-by-side assessment comparisons.
- `tests/`: System and unit tests for agent behaviors.

## Deployment (Azure)

Build and tag the container for Azure Container Registry (ACR):
```bash
docker build -t shl-agent .
docker tag shl-agent <registry>.azurecr.io/shl-agent
docker push <registry>.azurecr.io/shl-agent
```
Deploy the pushed image to Azure Container Apps or Azure App Service. Verify functionality via the `/health` and `/chat` endpoints on your public URL.
