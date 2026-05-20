import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


COLLECTION_NAME = os.getenv("COLLECTION_NAME", "megagym_exercises")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
QDRANT_PATH = os.getenv("QDRANT_PATH", "").strip()
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = _get_int_env("QDRANT_PORT", 6333)
TOP_K = _get_int_env("TOP_K", 5)


def create_qdrant_client() -> QdrantClient:
    if QDRANT_PATH:
        return QdrantClient(path=QDRANT_PATH)
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
