"""
AI Framework — Embeddings Module

File: guardian_ai/ai_framework/embeddings.py

Provides embedding generation for vector store operations.
Uses OpenAI embeddings by default, with fallback options.
"""

from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

_embedding_cache = {}


def get_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    cache_key = f"{model}:{text[:100]}"
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]

    try:
        import openai
        api_key = os.environ.get("OPENAI_API_KEY")

        if api_key:
            response = openai.Embedding.create(
                input=text,
                model=model
            )
            embedding = response['data'][0]['embedding']
            _embedding_cache[cache_key] = embedding
            return embedding

    except Exception as e:
        logger.warning(f"OpenAI embedding failed, using fallback: {e}")

    embedding = _generate_fallback_embedding(text)
    _embedding_cache[cache_key] = embedding
    return embedding


def _generate_fallback_embedding(text: str, dimensions: int = 1536) -> List[float]:
    import hashlib

    text_hash = hashlib.sha256(text.encode()).digest()

    seed = int.from_bytes(text_hash[:4], 'big')

    import random
    random.seed(seed)

    embedding = [random.gauss(0, 1) for _ in range(dimensions)]

    magnitude = sum(x ** 2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]

    return embedding


def get_embeddings_batch(texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    embeddings = []
    for text in texts:
        embedding = get_embedding(text, model)
        embeddings.append(embedding)
    return embeddings


def clear_embedding_cache() -> None:
    global _embedding_cache
    _embedding_cache.clear()
    logger.info("Embedding cache cleared")