from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

RETRIEVAL_SCRIPT = SCRIPTS_DIR / "evaluate_retrieval.py"
COMPARISON_SCRIPT = SCRIPTS_DIR / "compare_baseline_rag.py"


def _run_script(script_path: Path) -> int:
    result = subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_ROOT)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run project evaluation workflows for retrieval and baseline-vs-RAG comparison."
    )
    parser.add_argument(
        "--mode",
        choices=["all", "retrieval", "comparison"],
        default="all",
        help="Choose which evaluation workflow to run.",
    )
    args = parser.parse_args()

    if args.mode in {"all", "retrieval"}:
        print("Running retrieval evaluation...")
        retrieval_code = _run_script(RETRIEVAL_SCRIPT)
        if retrieval_code != 0:
            return retrieval_code

    if args.mode in {"all", "comparison"}:
        print("Running baseline-vs-RAG evaluation...")
        comparison_code = _run_script(COMPARISON_SCRIPT)
        if comparison_code != 0:
            return comparison_code

    print("Evaluation finished. Results are available in report/results/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())