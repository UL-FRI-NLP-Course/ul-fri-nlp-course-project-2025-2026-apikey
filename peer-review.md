# Peer Review HPC Run Guide

This guide shows how to run the Fitness RAG Assistant for peer review on Arnes
HPC.

The submitted project code and dataset are available in the shared ONJ project
directory:

```text
/d/hpc/projects/onj_fri/apikey
```

The app uses:

- Streamlit for the UI
- Ollama model `llama3.2:1b`
- Qdrant local storage for the per-user vector index
- MegaGym Exercise Dataset entries bundled with the HPC project copy

Do not run indexing, Ollama inference, or Streamlit on an HPC login node. Run
those steps inside a SLURM GPU allocation.

## 1. Log In To Arnes HPC

From your local laptop terminal, replace `<USERNAME>` with your Arnes username:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
```

Enter the Arnes verification code when prompted.

## 2. Open The Shared Project

On the HPC login node:

```bash
cd /d/hpc/projects/onj_fri/apikey
pwd
ls -la
```

The directory should contain files such as `app.py`, `requirements.txt`,
`scripts/`, `src/`, and `data/raw/megaGymDataset.csv`.

## 3. Prepare A Per-User Python Environment

The project code is shared. Keep the Python virtual environment in your HPC home
directory.

On the HPC login node:

```bash
cd /d/hpc/projects/onj_fri/apikey
mkdir -p "$HOME/models/ollama" "$HOME/.local" "$HOME/logs"
python3 -m venv "$HOME/apikey-venv"
source "$HOME/apikey-venv/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `$HOME/apikey-venv` already exists and already has the requirements
installed, activate it instead:

```bash
source "$HOME/apikey-venv/bin/activate"
```

## 4. Install Ollama If Needed

Check whether Ollama is already installed:

```bash
export PATH="$HOME/.local/bin:$PATH"
which ollama
```

If `which ollama` does not print a path, install Ollama without sudo on the HPC
login node:

```bash
cd ~
module load zstd/1.5.6-GCCcore-14.2.0
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst -o ollama-linux-amd64.tar.zst
tar --zstd -xf ollama-linux-amd64.tar.zst -C "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
which ollama
ollama --version
```

An Ollama warning about not connecting to a running server is expected at this
point.

## 5. Request A GPU Node

From the HPC login node:

```bash
cd /d/hpc/projects/onj_fri/apikey
salloc --partition=gpu --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=01:00:00
```

When the allocation is granted, enter the compute node:

```bash
srun --pty bash
pwd
hostname
nvidia-smi
```

The host should be a compute node such as `wn203.arnes.si`, not
`hpc-login*.arnes.si`.

## 6. Start Ollama On The GPU Node

Inside the GPU compute-node shell:

```bash
cd /d/hpc/projects/onj_fri/apikey
source "$HOME/apikey-venv/bin/activate"

export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
export QDRANT_PATH="$HOME/apikey_qdrant_storage"

mkdir -p logs
ollama serve > logs/ollama-${SLURM_JOB_ID}.log 2>&1 &
sleep 5
curl -s http://127.0.0.1:11434/api/tags
```

Pull the project model if it is not already listed:

```bash
ollama pull llama3.2:1b
ollama list
```

## 7. Build The Per-User Qdrant Index

Do this once per user, or repeat it if you want to rebuild the exercise index:

```bash
cd /d/hpc/projects/onj_fri/apikey
source "$HOME/apikey-venv/bin/activate"
export QDRANT_PATH="$HOME/apikey_qdrant_storage"
python scripts/index_megagym.py
```

Expected final line:

```text
Indexed 2918 exercises.
```

## 8. Run The Streamlit App

Keep Ollama running and start Streamlit on the GPU node:

```bash
cd /d/hpc/projects/onj_fri/apikey
source "$HOME/apikey-venv/bin/activate"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
export QDRANT_PATH="$HOME/apikey_qdrant_storage"

streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > logs/streamlit-${SLURM_JOB_ID}.log 2>&1 &
sleep 5
tail -n 30 logs/streamlit-${SLURM_JOB_ID}.log
hostname
```

The Streamlit log should show:

```text
URL: http://0.0.0.0:8501
```

Remember the short compute-node name from `hostname`. For example, if hostname
prints `wn203.arnes.si`, use `wn203` in the tunnel command below.

## 9. Open The UI From Your Laptop

Open a new local laptop terminal. Replace `<NODE>` with the short compute-node
name and `<USERNAME>` with your Arnes username:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  -L 8501:<NODE>:8501 \
  <USERNAME>@hpc-login.arnes.si
```

Keep the tunnel terminal open. Open this address in your laptop browser:

```text
http://127.0.0.1:8501
```

Example question:

```text
Which triceps exercises use a cable machine?
```

The app should answer and show retrieved exercise context.

## 10. Optional Retrieval Evaluation

Inside the GPU compute-node shell:

```bash
cd /d/hpc/projects/onj_fri/apikey
source "$HOME/apikey-venv/bin/activate"
export QDRANT_PATH="$HOME/apikey_qdrant_storage"
python scripts/run_evaluation.py --mode retrieval
```

The verified retrieval metrics are:

```text
Evaluated 11 retrieval queries
Hit@1: 0.636
Hit@3: 0.909
Hit@5: 0.909
Precision@5: 0.582
MRR: 0.742
```

## 11. Stop The Run

In the GPU compute-node shell:

```bash
pkill -f "streamlit run app.py"
pkill -f "ollama serve"
exit
```

Back on the HPC login node, cancel the interactive allocation. Replace
`<JOBID>` with the job ID printed by `salloc`:

```bash
scancel <JOBID>
squeue -j <JOBID>
```

Close the local SSH tunnel terminal with:

```bash
exit
```

## Later Runs

After the per-user virtual environment, Ollama model, and Qdrant index already
exist, repeat only these steps:

1. Log in to HPC.
2. Request a GPU node with `salloc` and enter it with `srun --pty bash`.
3. Run the exports and `ollama serve` commands from section 6.
4. Run Streamlit from section 8.
5. Open the SSH tunnel from section 9.

