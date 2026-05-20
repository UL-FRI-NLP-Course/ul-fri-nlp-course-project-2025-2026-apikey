# scripts/index_megagym.py

import os
import sys
from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Distance, VectorParams, PointStruct

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, create_qdrant_client

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "megaGymDataset.csv"

df = pd.read_csv(DATA_PATH).fillna("")

model = SentenceTransformer(EMBEDDING_MODEL)
client = create_qdrant_client()

FORCE_RECREATE_COLLECTION = os.getenv("FORCE_RECREATE_COLLECTION", "false").lower() in {
    "1",
    "true",
    "yes",
}
vector_params = VectorParams(size=384, distance=Distance.COSINE)

if FORCE_RECREATE_COLLECTION:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=vector_params,
    )
elif not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=vector_params,
    )

EMBED_BATCH_SIZE = 64
UPSERT_CHUNK_SIZE = 512

texts = []
payloads = []
ids = []

for idx, row in df.iterrows():
    text = f"""
Exercise: {row["Title"]}
Description: {row["Desc"]}
Type: {row["Type"]}
Body part: {row["BodyPart"]}
Equipment: {row["Equipment"]}
Difficulty level: {row["Level"]}
Rating: {row["Rating"]}
Rating description: {row["RatingDesc"]}
"""
    texts.append(text)
    ids.append(int(idx))
    payloads.append(
        {
            "title": row["Title"],
            "description": row["Desc"],
            "type": row["Type"],
            "body_part": row["BodyPart"],
            "equipment": row["Equipment"],
            "level": row["Level"],
            "rating": row["Rating"],
            "rating_desc": row["RatingDesc"],
            "text": text,
        }
    )

vectors = model.encode(texts, batch_size=EMBED_BATCH_SIZE, show_progress_bar=True)

for start in range(0, len(ids), UPSERT_CHUNK_SIZE):
    end = start + UPSERT_CHUNK_SIZE
    chunk_points = [
        PointStruct(id=ids[i], vector=vectors[i].tolist(), payload=payloads[i])
        for i in range(start, min(end, len(ids)))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=chunk_points)

print(f"Indexed {len(ids)} exercises.")
