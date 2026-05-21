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

# Quick Start Paths

Choose one execution path:

* **Local setup and run:** see `LOCAL_SETUP.md`
* **Arnes HPC setup and run:** see `ARNES_HPC_QUICKSTART.md`

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

