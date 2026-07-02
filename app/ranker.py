from typing import List, Dict, Any
import re

from app.logger import logger


class Ranker:
    """
    Simple production-ready ranker for assessment recommendations.
    Can later be upgraded to embeddings / ML ranking.
    """

    def __init__(self):
        # simple keyword boosts (you can expand this)
        self.boost_keywords = {
            "coding": ["java", "python", "c++", "coding", "programming"],
            "hr": ["interview", "hiring", "behavioral"],
            "java": ["java", "j2ee", "jee", "enterprise"]
        }

    def score_item(self, query: str, item: Dict[str, Any]) -> float:
        """
        Compute relevance score combining:
        embedding_similarity + keyword_score + category_score
        """
        embedding_similarity = float(item.get("embedding_similarity", 0.0))
        
        # 1. Calculate Keyword Score
        text = (item.get("name", "") + " " + item.get("description", "") + " " + item.get("url", "")).lower()
        query_lower = query.lower()
        
        query_tokens = set(re.findall(r"\w+", query_lower))
        text_tokens = set(re.findall(r"\w+", text))
        
        overlap = len(query_tokens & text_tokens)
        keyword_score = overlap * 2.0
        
        # Boost domain relevance
        for domain, keywords in self.boost_keywords.items():
            if any(k in query_lower for k in keywords) and any(k in text for k in keywords):
                keyword_score += 3.0
                
        # Generic HR mismatch penalty
        if "interview" in query_lower and "java" in text and "java" not in query_lower:
            keyword_score -= 1.5
            
        # 2. Calculate Category Score
        category_score = 0.0
        item_keys = [k.lower() for k in item.get("keys", [])]
        
        # Cognitive (Ability & Aptitude)
        if any(w in query_lower for w in ["cognitive", "aptitude", "ability", "reasoning", "logic"]):
            if any("ability" in k or "aptitude" in k for k in item_keys):
                category_score += 4.0
                
        # Personality (Personality & Behavior, situational, etc.)
        if any(w in query_lower for w in ["personality", "behavior", "situational", "opq"]):
            if any("personality" in k or "behavior" in k or "competency" in k or "situational" in k for k in item_keys):
                category_score += 4.0
                
        # Coding (Knowledge & Skills, programming)
        if any(w in query_lower for w in ["coding", "programming", "technical"]):
            if any("knowledge" in k or "skills" in k for k in item_keys):
                category_score += 4.0
                
        # Total combined score
        return embedding_similarity + keyword_score + category_score

    def rank(self, query: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Returns ranked items with score.
        """
        logger.info(f"Ranking {len(items)} items for query: '{query}'")
        
        scored = []
        for item in items:
            item_copy = dict(item)
            item_copy["score"] = self.score_item(query, item)
            scored.append(item_copy)

        # sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        top_name = scored[0]['name'] if scored else 'N/A'
        top_score = f"{scored[0]['score']:.2f}" if scored else '0.00'
        logger.info(f"Ranked items | Top: {top_name} (score={top_score})")

        return scored