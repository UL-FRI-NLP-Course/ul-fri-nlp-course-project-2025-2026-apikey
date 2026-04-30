#To primerja dva načina odgovarjanja.


# Prvi način je baseline:
# vprašanje -> Ollama -> odgovor

# Drugi način je RAG:
# vprašanje -> Qdrant najde relevantne vaje -> te vaje damo v prompt -> Ollama -> odgovor


# Pomembno: model je isti.
# V obeh primerih uporabljamo: llama3.1:8b

# Razlika je samo v tem, kaj model dobi kot input.
# Baseline dobi samo vprašanje.
# RAG dobi vprašanje + najdene vaje iz dataseta.
# Zato baseline odgovarja iz splošnega znanja, RAG pa naj bi odgovarjal bolj po našem datasetu.


from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.llm import ask_ollama  # noqa: E402
from src.rag import FitnessRAG, build_prompt  # noqa: E402

EVAL_PATH = PROJECT_ROOT / "data" / "eval" / "retrieval_eval.jsonl"
RESULTS_DIR = PROJECT_ROOT / "report" / "results"
MAX_EXAMPLES = 5


def _load_questions() -> list[dict[str, str]]:
    questions = []
    with EVAL_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                item = json.loads(line)
                questions.append({"id": item["id"], "question": item["question"]})
    return questions[:MAX_EXAMPLES]


def _baseline_prompt(question: str) -> str:
    return f"""
You are a helpful fitness assistant.

Answer the user's fitness question directly.
If you are uncertain, say so clearly.

Question:
{question}

Answer:
"""


def _write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "question", "baseline_answer", "rag_answer", "retrieved_context"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    lines = [
        "# Baseline vs RAG Examples",
        "",
        "Baseline answers are generated directly by the local LLM. RAG answers use the same LLM, but with retrieved MegaGym exercise entries added to the prompt.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['id']}",
                "",
                f"**Question:** {row['question']}",
                "",
                "**Baseline answer**",
                "",
                row["baseline_answer"].strip(),
                "",
                "**RAG answer**",
                "",
                row["rag_answer"].strip(),
                "",
                "**Retrieved context preview**",
                "",
                "```text",
                row["retrieved_context"].strip()[:1200],
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rag = FitnessRAG()
    rows = []

    for item in _load_questions():
        question = item["question"]
        print(f"Generating baseline and RAG answers for: {question}")
        context = rag.retrieve_context(question)
        baseline_answer = ask_ollama(_baseline_prompt(question))
        rag_answer = ask_ollama(build_prompt(question, context))
        rows.append(
            {
                "id": item["id"],
                "question": question,
                "baseline_answer": baseline_answer,
                "rag_answer": rag_answer,
                "retrieved_context": context,
            }
        )

    _write_csv(rows, RESULTS_DIR / "baseline_vs_rag_examples.csv")
    _write_markdown(rows, RESULTS_DIR / "baseline_vs_rag_examples.md")
    print(f"Wrote comparison examples to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
