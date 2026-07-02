import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from app.config import FAISS_PATH, CATALOG_PATH, TOP_K, RETRIEVAL_TOP_K
from app.logger import logger

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Loaded SentenceTransformer model (all-MiniLM-L6-v2)")

# Load catalog
with open(CATALOG_PATH, encoding="utf-8") as f:
    catalog = json.load(f)
logger.info(f"Loaded catalog with {len(catalog)} products from {CATALOG_PATH}")

# Load FAISS index
index = faiss.read_index(str(FAISS_PATH))
logger.info(f"Loaded FAISS index from {FAISS_PATH}")


class Retriever:
    """
    Semantic search retriever using FAISS + SentenceTransformer.
    Retrieves raw candidates (typically more than final TOP_K).
    """
    
    def __init__(self, k: int = None):
        """
        Initialize Retriever.
        
        Args:
            k: Number of results to retrieve (default: RETRIEVAL_TOP_K).
               Set higher than final TOP_K to allow ranker to refine.
        """
        self.k = k or RETRIEVAL_TOP_K
        logger.info(f"Initialized Retriever with k={self.k}")
    
    def get_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve raw candidate assessments via semantic similarity.
        
        Args:
            query: User query string
        
        Returns:
            List of product dictionaries from catalog (raw, unranked)
        """
        logger.info(f"Retrieving candidates for query: '{query}'")
        
        # Encode query
        query_embedding = model.encode(
            [query],
            normalize_embeddings=True
        )
        query_embedding = np.array(query_embedding, dtype=np.float32)
        
        # Search FAISS index
        D, I = index.search(query_embedding, self.k)
        
        # Collect results
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx != -1:
                item_copy = dict(catalog[idx])
                item_copy["embedding_similarity"] = float(dist)
                results.append(item_copy)
        
        logger.info(f"Retrieved {len(results)} raw candidates")
        return results


# Legacy function for backward compatibility
def search(query: str, k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Legacy search function. Use Retriever class for new code.
    
    Args:
        query: User query string
        k: Number of results to return
    
    Returns:
        List of product dictionaries
    """
    retriever = Retriever(k=k)
    return retriever.get_results(query)