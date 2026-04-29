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
* **Llama 3.1-8b** (via Ollama) as the language model
* **Streamlit** for the chat interface

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
├── app.py
├── docker-compose.yml
├── LICENSE
├── README.md
└── requirements.txt
```


---

# Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd ul-fri-nlp-course-project-2025-2026-apikey
```

---

## 2. Create virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `torchvision` is missing when running Streamlit:

```bash
pip install torchvision
```

---

## 4. Start Qdrant

The project requires a running local Qdrant instance.

Use the provided Docker Compose setup (recommended, pinned version with persistent storage):

```bash
docker compose up -d
```

If you prefer a one-off container without Compose:

```bash
docker run -p 6333:6333 qdrant/qdrant:v1.13.4
```

Qdrant will then be available at:

```text
http://localhost:6333
```

---

## Dataset

This project uses the MegaGym Exercise Dataset.

Download the dataset from the original source and place it at:

data/raw/megaGymDataset.csv

License: CC0 (Public Domain)

Original source:
https://www.kaggle.com/datasets/niharika41298/gym-exercise-data
---

# Indexing the Dataset

Before using the assistant, the dataset must be embedded and stored in Qdrant.

Run:

```bash
python scripts/index_megagym.py
```

This will:

* read the dataset
* generate embeddings
* create the Qdrant collection
* upload all exercise vectors

Expected output:

```text
Indexed XXXX exercises.
```

This step only needs to be done once.

---

# Running the Application

## Streamlit UI (recommended)

Run:

```bash
streamlit run app.py
```

This opens a browser-based chat interface where users can ask fitness-related questions.

Example questions:

* What exercises can I do for chest with dumbbells?
* How do I perform a Romanian deadlift correctly?
* What are good beginner back exercises?

---

# Example RAG Workflow

1. User asks a question
2. Question is embedded using Sentence Transformers
3. Qdrant retrieves the most relevant exercise entries
4. Retrieved context is passed to Llama 3.1 (via Ollama)
5. Final answer is generated using grounded context

This improves factual consistency compared to using the LLM alone.

---

