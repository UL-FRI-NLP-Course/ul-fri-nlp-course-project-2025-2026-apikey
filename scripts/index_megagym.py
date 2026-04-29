# src/index_megagym.py

import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "megaGymDataset.csv"
COLLECTION_NAME = "megagym_exercises"

df = pd.read_csv(DATA_PATH).fillna("")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

points = []

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

    vector = model.encode(text).tolist()

    points.append(
        PointStruct(
            id=int(idx),
            vector=vector,
            payload={
                "title": row["Title"],
                "description": row["Desc"],
                "type": row["Type"],
                "body_part": row["BodyPart"],
                "equipment": row["Equipment"],
                "level": row["Level"],
                "rating": row["Rating"],
                "rating_desc": row["RatingDesc"],
                "text": text,
            },
        )
    )

client.upsert(collection_name=COLLECTION_NAME, points=points)

print(f"Indexed {len(points)} exercises.")