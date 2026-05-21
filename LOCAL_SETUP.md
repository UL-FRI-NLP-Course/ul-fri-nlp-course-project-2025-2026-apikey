# Local Setup Guide

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd ul-fri-nlp-course-project-2025-2026-apikey
```

## 2. Create a virtual environment

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

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

If `torchvision` is missing when running Streamlit:

```bash
pip install torchvision
```

## 4. Download the dataset

This project uses the MegaGym Exercise Dataset.

Download it from:

https://www.kaggle.com/datasets/niharika41298/gym-exercise-data

Place the file here:

```text
data/raw/megaGymDataset.csv
```

License: CC0 (Public Domain)

## 5. Start Qdrant

Use the provided Docker Compose setup:

```bash
docker compose up -d
```

Qdrant should then be available at:

```text
http://localhost:6333
```

## 6. Start Ollama and pull the model

Make sure Ollama is installed and running locally, then pull the project model:

```bash
ollama pull llama3.2:1b
ollama list
```

Expected result: `llama3.2:1b` appears in the local model list.

## 7. Build the vector index

```bash
python scripts/index_megagym.py
```

Expected result:

```text
Indexed 2918 exercises.
```

## 8. Run retrieval evaluation

```bash
python scripts/evaluate_retrieval.py
```

This writes retrieval metrics to `report/results/`.

## 9. Run baseline vs RAG evaluation

```bash
python scripts/compare_baseline_rag.py
```

This writes comparison examples to `report/results/`.

## 10. Run the Streamlit app

```bash
streamlit run app.py
```

If `http://localhost:8501` does not open in your browser, try the `Network URL`
printed by Streamlit instead, for example `http://192.168.x.x:8501`. This can
happen on some Windows setups when `localhost` resolution or loopback handling
does not behave as expected, even though the Streamlit server is running
correctly.

Example questions:

* What exercises can I do for chest with dumbbells?
* Which triceps exercises use a cable machine?
* Give me beginner leg exercises using bodyweight.

## 11. What success looks like

The local path is working correctly when:

* Qdrant is reachable
* `llama3.2:1b` is installed in Ollama
* indexing completes successfully
* evaluation scripts write files into `report/results/`
* Streamlit answers questions and shows retrieved context