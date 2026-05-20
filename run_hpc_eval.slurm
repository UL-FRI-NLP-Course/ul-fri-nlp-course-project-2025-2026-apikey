#!/bin/bash
#SBATCH --job-name=fitness-rag-eval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/eval-%j.out
#SBATCH --error=logs/eval-%j.err

set -euo pipefail

cd "$HOME/rag-app"
mkdir -p logs

source .venv/bin/activate

export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"
export QDRANT_PATH="${QDRANT_PATH:-$HOME/rag-app/qdrant_storage}"

echo "Running on node: $(hostname)"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Model: ${OLLAMA_MODEL}"
nvidia-smi || true

ollama serve > "logs/ollama-${SLURM_JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill "$OLLAMA_PID" || true' EXIT

sleep 5
ollama pull "$OLLAMA_MODEL"
ollama ps || true

python scripts/index_megagym.py
python scripts/evaluate_retrieval.py
python scripts/compare_baseline_rag.py

echo "Results written to report/results"
