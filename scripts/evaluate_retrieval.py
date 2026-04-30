# ta datoteka dejansko testira zgolj kako dobro deluje iskanje po Qdrant. Vektorski bazi. Ne uporablja Llame in ne generira odgovorov. 
#flow je tak: vprašanje -> embedding -> Qdrant -> top 5 vaj -> preveri, ali so relevantne


#primer: 
#Vprašanje: What chest exercises can I do with dumbbells?
#odgovor: 
# Dumbbell chest fly
# Dumbbell bench press
# Dumbbell Flyes
# ...


# Skripta preveri:

# ali je BodyPart = Chest
# ali je Equipment = Dumbbell
# ali se pojavi keyword press ali fly
# Potem izračuna metrike:

# Hit@1: ali je prvi rezultat dober?
# Hit@3: ali je vsaj eden med prvimi 3 dober?
# Hit@5: ali je vsaj eden med prvimi 5 dober?
# Precision@5: koliko od prvih 5 je dobrih?
# MRR: kako visoko se pojavi prvi dober rezultat?
# To je test: ali retrieval najde prave vaje.



from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_HOST, QDRANT_PORT, TOP_K  # noqa: E402

EVAL_PATH = PROJECT_ROOT / "data" / "eval" / "retrieval_eval.jsonl"
RESULTS_DIR = PROJECT_ROOT / "report" / "results"
TOP_K_EVAL = max(5, TOP_K)


@dataclass
# to je rezultat evalvacije za eno vprašanje
class EvalResult:
    query_id: str
    question: str
    hit_at_1: bool
    hit_at_3: bool
    hit_at_5: bool
    precision_at_5: float
    reciprocal_rank: float
    top_titles: str


# to je funkcija, ki pretvori vrednost v seznam besed
def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text.lower()] if text else []

# to je funkcija, ki preveri, ali je vrednost relevantna
def _matches_expected(payload: dict[str, Any], spec: dict[str, Any]) -> bool:
    body_parts = _as_list(spec.get("expected_body_part"))
    equipment = _as_list(spec.get("expected_equipment"))
    levels = _as_list(spec.get("expected_level"))
    keywords = _as_list(spec.get("expected_keywords"))

    payload_body_part = str(payload.get("body_part", "")).strip().lower()
    payload_equipment = str(payload.get("equipment", "")).strip().lower()
    payload_level = str(payload.get("level", "")).strip().lower()
    searchable_text = " ".join(
        [
            str(payload.get("title", "")),
            str(payload.get("description", "")),
            str(payload.get("text", "")),
        ]
    ).lower()

    body_part_ok = not body_parts or payload_body_part in body_parts
    equipment_ok = not equipment or payload_equipment in equipment
    level_ok = not levels or payload_level in levels
    keyword_ok = not keywords or any(keyword in searchable_text for keyword in keywords)

    return body_part_ok and equipment_ok and level_ok and keyword_ok

# to je funkcija, ki naloži testne vprašanja
def _load_eval_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases

# to je funkcija, ki zapiše rezultate v CSV datoteko
def _write_csv(results: list[EvalResult], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "query_id",
                "question",
                "hit_at_1",
                "hit_at_3",
                "hit_at_5",
                "precision_at_5",
                "reciprocal_rank",
                "top_titles",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)

# to je funkcija, ki zapiše rezultate v Markdown datoteko
def _write_markdown(results: list[EvalResult], path: Path) -> None:
    count = len(results)
    hit_at_1 = sum(result.hit_at_1 for result in results) / count
    hit_at_3 = sum(result.hit_at_3 for result in results) / count
    hit_at_5 = sum(result.hit_at_5 for result in results) / count
    precision_at_5 = sum(result.precision_at_5 for result in results) / count
    mrr = sum(result.reciprocal_rank for result in results) / count

    lines = [
        "# Retrieval Evaluation",
        "",
        "This lightweight evaluation checks whether the top retrieved exercises match manually defined expectations for body part, equipment, difficulty level, and exercise keywords.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Queries | {count} |",
        f"| Hit@1 | {hit_at_1:.3f} |",
        f"| Hit@3 | {hit_at_3:.3f} |",
        f"| Hit@5 | {hit_at_5:.3f} |",
        f"| Precision@5 | {precision_at_5:.3f} |",
        f"| MRR | {mrr:.3f} |",
        "",
        "## Query Details",
        "",
        "| ID | Hit@5 | Precision@5 | Top Retrieved Exercises |",
        "| --- | ---: | ---: | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.query_id} | {int(result.hit_at_5)} | {result.precision_at_5:.2f} | {result.top_titles} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

# to je glavna funkcija, ki izvaja evalvacijo
def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cases = _load_eval_cases(EVAL_PATH)

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    results: list[EvalResult] = []
    for case in cases:
        query_vector = model.encode(case["question"]).tolist()
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=TOP_K_EVAL,
        )
        points = response.points
        relevance = [_matches_expected(point.payload or {}, case) for point in points]
        relevant_ranks = [index + 1 for index, is_relevant in enumerate(relevance) if is_relevant]
        top_five = points[:5]
        top_five_relevance = relevance[:5]
        top_titles = "; ".join(str((point.payload or {}).get("title", "")) for point in top_five)

        results.append(
            EvalResult(
                query_id=case["id"],
                question=case["question"],
                hit_at_1=any(relevance[:1]),
                hit_at_3=any(relevance[:3]),
                hit_at_5=any(relevance[:5]),
                precision_at_5=sum(top_five_relevance) / len(top_five_relevance) if top_five_relevance else 0.0,
                reciprocal_rank=1 / relevant_ranks[0] if relevant_ranks else 0.0,
                top_titles=top_titles,
            )
        )

    _write_csv(results, RESULTS_DIR / "retrieval_eval_results.csv")
    _write_markdown(results, RESULTS_DIR / "retrieval_eval_results.md")

    count = len(results)
    print(f"Evaluated {count} retrieval queries")
    print(f"Hit@1: {sum(result.hit_at_1 for result in results) / count:.3f}")
    print(f"Hit@3: {sum(result.hit_at_3 for result in results) / count:.3f}")
    print(f"Hit@5: {sum(result.hit_at_5 for result in results) / count:.3f}")
    print(f"Precision@5: {sum(result.precision_at_5 for result in results) / count:.3f}")
    print(f"MRR: {sum(result.reciprocal_rank for result in results) / count:.3f}")
    print(f"Wrote results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
