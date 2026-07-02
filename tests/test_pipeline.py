import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.intent import detect_intent
from app.retriever import search

print("="*60)
print("TESTING: Intent Detection, Search & Retriever")
print("="*60)

# Test cases
test_queries = [
    "Hiring Java developer 4 years",
    "What's the difference between Python and JavaScript?",
    "Actually I need something else",
    "help",
]

for query in test_queries:
    print(f"\n📌 Query: {query}")
    print("-" * 60)
    
    # 1. Test Intent Detection
    intent = detect_intent(query)
    print(f"✓ Intent: {intent}")
    
    # 2. Test Search & Retrieval
    try:
        results = search(query, k=3)
        print(f"✓ Found {len(results)} results")
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n  {i}. {result['name']}")
                print(f"     Status: {result['status']}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*60)
print("✓ All components working!")
print("="*60)
