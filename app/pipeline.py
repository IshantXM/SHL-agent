"""
Main processing pipeline: Retrieval → Ranking → Response.

This module demonstrates the recommended pattern:
  1. Retriever.get_results(query) → raw candidates (many)
  2. Ranker.rank(query, candidates) → scored/sorted (all)
  3. Take top-k → final recommendations
  4. Build response
"""

from typing import Dict, Any, List

from app.retriever import Retriever
from app.ranker import Ranker
from app.config import TOP_K
from app.logger import logger


# Initialize once
retriever = Retriever()
ranker = Ranker()


def process_query(query: str) -> Dict[str, Any]:
    """
    Process user query through retrieval + ranking pipeline.
    
    Step-by-step:
      1. Raw retrieval: Get candidates from FAISS semantic search
      2. Ranking: Score candidates using keyword matching + domain logic
      3. Top-k selection: Take best TOP_K results
      4. Response building: Format for API response
    
    Args:
        query: User query string (e.g., "Hiring Java developer 5 years")
    
    Returns:
        Dictionary with:
          - reply: Summary message
          - recommendations: Top-k scored assessments
          - raw_count: Total candidates retrieved
          - ranked_count: Candidates after ranking
    """
    logger.info(f"[PIPELINE] Starting query processing: '{query}'")
    
    # Step 1: RETRIEVAL - Get raw candidates from semantic search
    logger.info("[PIPELINE] Step 1: Retrieval - Fetching raw candidates...")
    raw_results = retriever.get_results(query)
    raw_count = len(raw_results)
    
    if not raw_results:
        logger.warning("[PIPELINE] No candidates retrieved!")
        return {
            "reply": "No matching assessments found.",
            "recommendations": [],
            "raw_count": 0,
            "ranked_count": 0,
            "error": "No candidates retrieved"
        }
    
    # Step 2: RANKING - Score and sort candidates
    logger.info("[PIPELINE] Step 2: Ranking - Scoring candidates...")
    ranked_results = ranker.rank(query, raw_results)
    ranked_count = len(ranked_results)
    
    # Step 3: TOP-K SELECTION - Take best results
    logger.info(f"[PIPELINE] Step 3: Top-K Selection - Taking top {TOP_K} from {ranked_count}")
    top_k = ranked_results[:TOP_K]
    
    # Step 4: RESPONSE BUILDING
    logger.info("[PIPELINE] Step 4: Building response...")
    response = {
        "reply": f"Found {len(top_k)} matching assessments for your query.",
        "recommendations": [
            {
                "name": item.get("name", "Unknown"),
                "url": item.get("link", ""),
                "test_type": item.get("description", "Assessment")[:50],  # Short snippet
                "score": item.get("score", 0.0)
            }
            for item in top_k
        ],
        "raw_count": raw_count,
        "ranked_count": ranked_count,
        "metadata": {
            "retriever_k": retriever.k,
            "ranker_top_k": TOP_K,
            "avg_score": sum(item.get("score", 0) for item in top_k) / len(top_k) if top_k else 0
        }
    }
    
    logger.info(f"[PIPELINE] Complete | Retrieved: {raw_count}, Ranked: {ranked_count}, Final: {len(top_k)}")
    
    return response
