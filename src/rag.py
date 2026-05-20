from sentence_transformers import SentenceTransformer
from src.config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
    create_qdrant_client,
)


class FitnessRAG:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = create_qdrant_client()

    def retrieve_context(self, question: str, top_k: int = TOP_K) -> str:
        query_vector = self.model.encode(question).tolist()

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        )

        return "\n\n".join(point.payload["text"] for point in results.points)


def build_prompt(question: str, context: str) -> str:
    return f"""
You are a helpful fitness assistant.

Use only the retrieved exercise database entries to answer.
Prefer exercises where body part, equipment, and difficulty match the question.
Remove duplicate or near-duplicate exercises.

For each exercise, include:
- Exercise name
- Why it matches the question
- Short explanation
- Difficulty level if available

Do not invent unsupported exercises.
If the dataset does not contain enough information, say so clearly.

Retrieved exercise entries:
{context}

Question:
{question}

Answer:
"""
