"""
Vector Store — Agentic RAG using ChromaDB

File: guardian_ai/memory/vector_store.py

Provides semantic search and document embedding storage for deal context,
email threads, and historical patterns. Used by the LLM for context-aware responses.
"""

from typing import Optional, List, Dict, Any
import logging

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

logger = logging.getLogger(__name__)


class VectorStoreManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        if chromadb is None:
            raise ImportError(
                "ChromaDB is not installed. Run: pip install chromadb"
            )

        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collections = {}

    def initialize_collection(self, collection_name: str, metadata: Optional[dict] = None) -> Any:
        try:
            existing = self.client.get_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' already exists")
            self.collections[collection_name] = existing
            return existing
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                metadata=metadata or {"description": f"Vector store for {collection_name}"}
            )
            self.collections[collection_name] = collection
            logger.info(f"Created new collection: {collection_name}")
            return collection

    def get_collection(self, collection_name: str) -> Any:
        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(name=collection_name)
            self.collections[collection_name] = collection
            return collection
        except Exception as e:
            logger.error(f"Collection '{collection_name}' not found: {e}")
            return None

    def store_document_embedding(
        self,
        deal_id: str,
        document_text: str,
        metadata: dict,
        collection_name: str = "deal_documents"
    ) -> Dict[str, Any]:
        collection = self.get_collection(collection_name)
        if not collection:
            collection = self.initialize_collection(collection_name)

        chunks = self._chunk_text(document_text, max_tokens=512, overlap=0.2)

        embeddings = []
        chunk_ids = []
        chunk_metadata_list = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{deal_id}_doc_{metadata.get('document_id', 'unknown')}_{i}"
            chunk_ids.append(chunk_id)

            chunk_metadata = {
                **metadata,
                "deal_id": deal_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            }
            chunk_metadata_list.append(chunk_metadata)

            try:
                from guardian_ai.ai_framework.embeddings import get_embedding
                embedding = get_embedding(chunk)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Could not generate embedding for chunk {i}: {e}")
                continue

        if not embeddings:
            return {"error": "No embeddings generated", "chunks_processed": 0}

        try:
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata_list
            )

            logger.info(f"Stored {len(chunks)} document chunks for deal {deal_id}")

            return {
                "success": True,
                "deal_id": deal_id,
                "chunks_stored": len(chunks),
                "document_id": metadata.get("document_id")
            }
        except Exception as e:
            logger.error(f"Error storing document embedding: {e}")
            return {"error": str(e), "chunks_processed": len(chunks)}

    def store_email_embedding(
        self,
        deal_id: str,
        email_content: str,
        metadata: dict,
        collection_name: str = "deal_emails"
    ) -> Dict[str, Any]:
        collection = self.get_collection(collection_name)
        if not collection:
            collection = self.initialize_collection(collection_name)

        chunks = self._chunk_text(email_content, max_tokens=512, overlap=0.2)

        embeddings = []
        chunk_ids = []
        chunk_metadata_list = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{deal_id}_email_{metadata.get('email_id', 'unknown')}_{i}"
            chunk_ids.append(chunk_id)

            chunk_metadata = {
                **metadata,
                "deal_id": deal_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "channel": "email"
            }
            chunk_metadata_list.append(chunk_metadata)

            try:
                from guardian_ai.ai_framework.embeddings import get_embedding
                embedding = get_embedding(chunk)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Could not generate embedding for chunk {i}: {e}")
                continue

        if not embeddings:
            return {"error": "No embeddings generated", "chunks_processed": 0}

        try:
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata_list
            )

            logger.info(f"Stored {len(chunks)} email chunks for deal {deal_id}")

            return {
                "success": True,
                "deal_id": deal_id,
                "chunks_stored": len(chunks),
                "email_id": metadata.get("email_id")
            }
        except Exception as e:
            logger.error(f"Error storing email embedding: {e}")
            return {"error": str(e)}

    def semantic_search(
        self,
        query: str,
        deal_id: Optional[str] = None,
        n_results: int = 5,
        collection_name: str = "deal_documents"
    ) -> List[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        if not collection:
            logger.warning(f"Collection '{collection_name}' not found for semantic search")
            return []

        try:
            from guardian_ai.ai_framework.embeddings import get_embedding
            query_embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Could not generate query embedding: {e}")
            return []

        where_filter = {"deal_id": deal_id} if deal_id else None

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )

            if not results or not results.get('documents'):
                return []

            search_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results.get('metadatas', [[]])[0],
                results.get('distances', [[]])[0]
            )):
                search_results.append({
                    "rank": i + 1,
                    "text": doc,
                    "metadata": metadata,
                    "relevance_score": 1 - distance if distance else None,
                    "deal_id": metadata.get('deal_id') if metadata else None
                })

            logger.info(f"Semantic search returned {len(search_results)} results for query")

            return search_results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    def get_deal_context_for_llm(self, deal_id: str, max_chunks: int = 10) -> str:
        doc_results = self.semantic_search(
            query="",
            deal_id=deal_id,
            n_results=max_chunks,
            collection_name="deal_documents"
        )

        email_results = self.semantic_search(
            query="",
            deal_id=deal_id,
            n_results=max_chunks,
            collection_name="deal_emails"
        )

        all_results = doc_results + email_results

        all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        context_parts = []
        for result in all_results[:max_chunks]:
            source = result['metadata'].get('document_type', 'document') if result['metadata'] else 'document'
            text = result['text']

            context_parts.append(f"[{source.upper()}] {text}")

        if not context_parts:
            return "No relevant context found for this deal."

        context = "\n\n---\n\n".join(context_parts)

        return f"## Relevant Deal Context\n\n{context}\n\n---\n*End of retrieved context*"

    def _chunk_text(self, text: str, max_tokens: int = 512, overlap: float = 0.2) -> List[str]:
        if not text:
            return []

        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = []
        current_tokens = 0

        overlap_sentences = int(len(sentences) * overlap) if len(sentences) > 3 else 1

        for i, sentence in enumerate(sentences):
            sentence_tokens = len(sentence.split())

            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
                current_tokens = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')

        return [c for c in chunks if c.strip()]

    def delete_deal_vectors(self, deal_id: str, collection_name: str = "deal_documents") -> bool:
        collection = self.get_collection(collection_name)
        if not collection:
            return False

        try:
            collection.delete(where={"deal_id": deal_id})
            logger.info(f"Deleted all vectors for deal {deal_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting deal vectors: {e}")
            return False

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        collection = self.get_collection(collection_name)
        if not collection:
            return {"error": "Collection not found"}

        try:
            count = collection.count()
            return {
                "collection_name": collection_name,
                "total_vectors": count
            }
        except Exception as e:
            return {"error": str(e)}


vector_store = VectorStoreManager()


def initialize_collection(collection_name: str) -> Any:
    return vector_store.initialize_collection(collection_name)


def store_document_embedding(deal_id: str, document_text: str, metadata: dict) -> Dict[str, Any]:
    return vector_store.store_document_embedding(deal_id, document_text, metadata)


def store_email_embedding(deal_id: str, email_content: str, metadata: dict) -> Dict[str, Any]:
    return vector_store.store_email_embedding(deal_id, email_content, metadata)


def semantic_search(query: str, deal_id: str = None, n_results: int = 5) -> List[Dict[str, Any]]:
    return vector_store.semantic_search(query, deal_id, n_results)


def get_deal_context_for_llm(deal_id: str) -> str:
    return vector_store.get_deal_context_for_llm(deal_id)