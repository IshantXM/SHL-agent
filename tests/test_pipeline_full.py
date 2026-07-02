"""
Test the full retrieval → ranking → response pipeline.

Demonstrates the recommended pattern:
  retriever.get_results() → raw candidates (many)
  ranker.rank() → scored/sorted (all)
  [:TOP_K] → final recommendations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.retriever import Retriever
from app.ranker import Ranker
from app.config import TOP_K, RETRIEVAL_TOP_K
from app.logger import logger

# Initialize components
retriever = Retriever()
ranker = Ranker()


def test_full_pipeline():
    """Test the complete retrieval + ranking pipeline."""
    
    test_queries = [
        "Hiring Java developer 4 years",
        "Need Python engineer with AWS",
        "Looking for DevOps architect",
        "QA specialist with test automation",
    ]
    
    print("\n" + "="*80)
    print("FULL PIPELINE TEST: Retrieval -> Ranking -> Top-K")
    print("="*80)
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        # STEP 1: Raw retrieval (fetch more candidates)
        print(f"\n[STEP 1] RETRIEVAL: Fetching {RETRIEVAL_TOP_K} raw candidates...")
        raw_results = retriever.get_results(query)
        print(f"  Retrieved {len(raw_results)} candidates")
        
        if raw_results:
            print(f"  First raw result: {raw_results[0]['name']}")
        
        # STEP 2: Ranking (score all candidates)
        print(f"\n[STEP 2] RANKING: Scoring {len(raw_results)} candidates...")
        ranked_results = ranker.rank(query, raw_results)
        print(f"  Ranked {len(ranked_results)} candidates")
        
        if ranked_results:
            print(f"  Top candidate after ranking: {ranked_results[0]['name']} (score: {ranked_results[0]['score']:.2f})")
        
        # STEP 3: Take top-k
        print(f"\n[STEP 3] TOP-K SELECTION: Taking top {TOP_K}...")
        top_k = ranked_results[:TOP_K]
        print(f"  Final recommendations: {len(top_k)}")
        
        # STEP 4: Display results
        print(f"\n[STEP 4] FINAL RESULTS:")
        print(f"  Retrieved: {len(raw_results)} | Ranked: {len(ranked_results)} | Final: {len(top_k)}")
        print(f"\n  Top Recommendations:")
        
        for i, item in enumerate(top_k, 1):
            score = item.get("score", 0)
            name = item.get("name", "Unknown")
            status = item.get("status", "")
            print(f"    {i}. {name}")
            print(f"       Score: {score:.2f} | Status: {status}")
        
        # Calculate average score
        avg_score = sum(item.get("score", 0) for item in top_k) / len(top_k) if top_k else 0
        print(f"\n  Average Score: {avg_score:.2f}")


if __name__ == "__main__":
    test_full_pipeline()
    print("\n" + "="*80)
    print("Pipeline test complete!")
    print("="*80 + "\n")
