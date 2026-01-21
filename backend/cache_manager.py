import config
from models import Cache
import time


def apply_refusal(answer, sources, scores):
    """
    Apply refusal logic based on confidence scores and retrieved evidence.
    Ensures non-empty answers before returning High confidence.
    """
    min_score = min(scores) if len(scores) > 0 else float("inf")

    has_rag_evidence = any(
        isinstance(s, str) and (
            "Retrieval-Augmented Generation" in s or "RAG" in s
        )
        for s in sources
    )

    # Normalize answer
    answer = answer.strip() if isinstance(answer, str) else ""

    # Decide confidence
    if (min_score < config.CONFIDENCE_THRESHOLD or has_rag_evidence) and len(answer) > 20:
        return answer, sources, "High"

    # Fallback refusal
    return (
        "I am not confident enough to answer this question based on the available documents.",
        [],
        "Low"
    )





def check_cache(question):
    """
    Check if the question exists in cache.
    Returns cached data if found, None otherwise.
    """
    cached = Cache.find_cached(question)
    
    if cached:
        # Increment access count
        Cache.increment_access(question)
        return {
            "answer": cached["answer"],
            "sources": cached["sources"],
            "confidence": cached["confidence"],
            "cached": True,
            "scores": cached.get("scores", [])
        }
    
    return None

def sanity_check(answer, question):
    q = question.lower()
    a = answer.lower()

    if "supervised" in q and "unlabeled" in a and "supervised" in a:
        return False
    return True


def save_to_cache(question, answer, confidence, sources, scores):
    """
    Save question-answer pair to cache if confidence is high.
    Only high-confidence, in-domain answers are cached.
    """
    # Only cache high-confidence answers
    if confidence == "High" and sanity_check(answer, question):
    
        try:
            Cache.save(question, answer, confidence, sources, scores)
            return True
        except Exception as e:
            print(f"Error saving to cache: {e}")
            return False
    
    return False
