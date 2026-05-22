# Domain-Specific Fitness NLP Assistant Using Retrieval-Augmented Generation (RAG)

**Authors:**
Domen Pahole,
Luka Rizman,
Nina Trivić

---

# Project Overview

This project is a domain-specific AI fitness assistant built for the Natural Language Processing course.

The goal is to create a conversational assistant specialized in fitness knowledge, capable of answering questions about:

* exercises
* workout techniques
* muscle groups
* equipment usage
* training recommendations
* basic fitness guidance

Instead of relying only on a general-purpose LLM, the system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant exercise information from a structured fitness dataset and provide more grounded, domain-specific answers.

The project uses:

* **Qdrant** as a vector database
* **Sentence Transformers** for embeddings
* **Llama 3.2-1b** (via Ollama) as the language model
* **Streamlit** for the chat interface

---

# Evaluation

The repository includes two evaluation workflows:

* **Retrieval evaluation** measures whether Qdrant returns relevant exercises for a query using metrics such as Hit@1, Hit@3, Hit@5, Precision@5, and MRR.
* **Baseline vs RAG comparison** generates example answers with and without retrieved context so the effect of RAG can be inspected qualitatively.

Run both with:

```bash
python scripts/run_evaluation.py
```

Or run only one part:

```bash
python scripts/run_evaluation.py --mode retrieval
python scripts/run_evaluation.py --mode comparison
```

Generated outputs are written to `report/results/`.

---

# Quick Start Paths

Choose one execution path:

* **Local setup and run:** see `LOCAL_SETUP.md`
* **Arnes HPC setup and run:** see `ARNES_HPC_QUICKSTART.md`
* **Peer review on Arnes HPC:** see `peer-review.md`

---

# Verified Arnes HPC Run

The submitted HPC copy is available at:

```text
/d/hpc/projects/onj_fri/apikey
```

The verified HPC setup keeps the shared project code there and uses per-user
runtime paths for the Python environment and Qdrant index:

```text
$HOME/apikey-venv
$HOME/apikey_qdrant_storage
```

After Arnes SSH/OTP login, use `ARNES_HPC_QUICKSTART.md` for the full setup and
run procedure. The core GPU-node commands are:

```bash
cd /d/hpc/projects/onj_fri/apikey
source "$HOME/apikey-venv/bin/activate"
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
export QDRANT_PATH="$HOME/apikey_qdrant_storage"
python scripts/index_megagym.py
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Run these commands inside a SLURM GPU allocation, not on the HPC login node.

---

# Repository Structure

```text
.
├── .streamlit/
│   └── config.toml
│
├── .venv/
│
├── data/
│   ├── raw/
│   │   └── (place megaGymDataset.csv here after downloading)
│   └── README.md
│
├── report/
│   ├── code/
│   ├── ds_report.cls
│   ├── logo.png
│   ├── report.bib
│   ├── report.pdf
│   └── report.tex
│
├── scripts/
│   └── index_megagym.py
│
├── src/
│   ├── config.py
│   ├── llm.py
│   └── rag.py
│
├── .gitignore
├── ARNES_HPC_QUICKSTART.md
├── LOCAL_SETUP.md
├── app.py
├── docker-compose.yml
├── LICENSE
├── README.md
└── requirements.txt
```


# Example RAG Workflow

1. User asks a question
2. Question is embedded using Sentence Transformers
3. Qdrant retrieves the most relevant exercise entries
4. Retrieved context is passed to Llama 3.2 1B (via Ollama)
5. Final answer is generated using grounded context

This improves factual consistency compared to using the LLM alone.

---
