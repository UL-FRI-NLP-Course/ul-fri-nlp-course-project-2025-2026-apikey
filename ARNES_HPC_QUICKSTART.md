# Arnes HPC Quickstart

This guide starts after you pull the repository. It shows how to run the final
Fitness RAG assistant on Arnes HPC with:

- Streamlit UI
- Ollama model `llama3.2:1b`
- local Qdrant storage through `QDRANT_PATH`
- MegaGym exercise dataset indexing
- retrieval and baseline-vs-RAG evaluation

**Note:** this quickstart assumes a Bash/Linux-style shell for the commands shown
below. The remote HPC commands run on Linux. If you are using Windows
PowerShell on your laptop, some local commands such as `test -f`, `pbcopy`,
`rsync`, `~/.ssh/...`, and `&&` or `||` will need PowerShell equivalents or a
Unix-like shell such as Git Bash or WSL.

Replace `<USERNAME>` with your Arnes username.

## 1. Local Pull

On your laptop:

```bash
git clone <REPOSITORY_URL>
cd ul-fri-nlp-course-project-2025-2026-apikey
```

If you already cloned it:

```bash
cd ul-fri-nlp-course-project-2025-2026-apikey
git pull
```

## 2. One-Time Arnes SSH And OTP Setup

Check whether you already have an SSH public key:

```bash
test -f ~/.ssh/id_ed25519.pub && echo "SSH public key exists" || echo "No default SSH public key"
```

If it does not exist:

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Copy the public key:

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

Open:

```text
https://fido.sling.si/
```

Add the copied public key under your user settings, in `SSH public keys`, then
save the profile.

Configure the Arnes HPC OTP token through the special OTP host:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-otp.arnes.si
```

Scan the QR code shown in the terminal with Google Authenticator. Use this
6-digit code for future HPC SSH logins.

Test login:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
```

Expected result:

```text
Verification code:
Prijavno vozlišče Arnesove HPC gruče
[<USERNAME>@hpc-login... ~]$
```

Then:

```bash
hostname
pwd
exit
```

Do not run model inference, indexing, or Streamlit on the login node. Use the
login node only for setup and SLURM commands.

## 3. Upload Project To The HPC Home Directory

This guide uses `~/rag-app` in the user's HPC home directory as the working
project location. If your course setup later uses a shared project directory,
adapt the paths in this guide accordingly.

From your laptop, inside the repository root:

```bash
rsync -av \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "venv" \
  --exclude "__pycache__" \
  --exclude ".pytest_cache" \
  --exclude ".ollama" \
  --exclude "logs" \
  ./ <USERNAME>@hpc-login.arnes.si:~/rag-app/
```

Expected result ends with something like:

```text
sent ... bytes  received ... bytes
total size is ...
```

After upload, login:


```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
```

Go to the prepared project directory:

```bash
cd ~/rag-app
ls -la
```

Expected result: the directory contains files such as:

```text
app.py
requirements.txt
src/
scripts/
data/
report/
ARNES_HPC_QUICKSTART.md
```

If your deployment moves to `/d/hpc/projects/onj_fri/apikey`, update the paths
in this guide from `~/rag-app` to that shared project path.

## 4. Prepare Python Environment On HPC

This step is only needed once per user/HPC copy. If `.venv` already exists in
`~/rag-app`, skip to step 5.

Check:

```bash
cd ~/rag-app
test -d .venv && echo "venv exists" || echo "venv missing"
```

If it is missing, prepare directories and install Python dependencies:

```bash
mkdir -p ~/rag-app ~/models/ollama ~/.local ~/logs
cd ~/rag-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Expected result:

```text
Successfully installed ... streamlit ... sentence-transformers ... qdrant-client
```

## 5. Install Ollama Without Sudo

On the HPC login node:

```bash
cd ~
module load zstd/1.5.6-GCCcore-14.2.0
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst -o ollama-linux-amd64.tar.zst
tar --zstd -xf ollama-linux-amd64.tar.zst -C ~/.local
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
which ollama
ollama --version
```

Expected result:

```text
~/.local/bin/ollama
Warning: could not connect to a running Ollama instance
Warning: client version is ...
```

The warning is normal because the Ollama server is not running yet.

Save the environment variables for future shell sessions:

```bash
grep -q 'OLLAMA_MODELS' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
EOF
```

## 6. Start An Interactive GPU Session

From the HPC login node:

```bash
salloc --partition=gpu --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=02:00:00
```

When allocation is granted, enter the compute node:

```bash
srun --pty bash
```

Check that you are on a GPU node:

```bash
hostname
nvidia-smi
```

Expected result:

```text
wn...arnes.si
NVIDIA-SMI ...
Tesla V100S-PCIE-32GB
```

## 7. Start Ollama And Pull The Final Model

Inside the GPU node shell:

```bash
cd ~/rag-app
source .venv/bin/activate
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
mkdir -p logs
ollama serve > logs/ollama-${SLURM_JOB_ID}.log 2>&1 &
sleep 5
curl -s http://127.0.0.1:11434/api/tags
```

Expected result:

```json
{"models":[]}
```

Pull the final model:

```bash
ollama pull llama3.2:1b
ollama list
```

Expected result:

```text
NAME            ID              SIZE
llama3.2:1b     ...             ...
```

Test GPU inference:

```bash
ollama run llama3.2:1b "Answer in one sentence: what is a dumbbell chest press?"
ollama ps
```

Expected result:

```text
PROCESSOR    100% GPU
```

## 8. Build The Local Qdrant Index

Inside the GPU node shell:

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
python scripts/index_megagym.py
```

Expected result:

```text
Batches: 100%|...
Indexed 2918 exercises.
```

This creates a persistent local Qdrant database at:

```text
~/rag-app/qdrant_storage
```

## 9. Run Retrieval Evaluation

Inside the GPU node shell:

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
python scripts/evaluate_retrieval.py
```

Expected result from the verified HPC run:

```text
Evaluated 11 retrieval queries
Hit@1: 0.636
Hit@3: 0.909
Hit@5: 0.909
Precision@5: 0.582
MRR: 0.742
Wrote results to /d/hpc/home/<USERNAME>/rag-app/report/results
```

## 10. Run Baseline Vs RAG Evaluation

Make sure Ollama is still running, then:

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
python scripts/compare_baseline_rag.py
```

Expected result:

```text
Generating baseline and RAG answers for: ...
Wrote comparison examples to /d/hpc/home/<USERNAME>/rag-app/report/results
```

The output files are:

```text
report/results/retrieval_eval_results.md
report/results/retrieval_eval_results.csv
report/results/baseline_vs_rag_examples.md
report/results/baseline_vs_rag_examples.csv
```

## 11. Run The Streamlit UI

Inside the GPU node shell, keep Ollama running and start Streamlit:

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > logs/streamlit-${SLURM_JOB_ID}.log 2>&1 &
sleep 5
tail -n 30 logs/streamlit-${SLURM_JOB_ID}.log
```

Expected result:

```text
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:8501
```

Find the compute node name:

```bash
hostname
```

Example:

```text
wn203.arnes.si
```

From a new local laptop terminal, open an SSH tunnel through the login node. Use
the short node name, for example `wn203`:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  -L 8501:wn203:8501 \
  <USERNAME>@hpc-login.arnes.si
```

Keep this terminal open. Then open in your laptop browser:

```text
http://127.0.0.1:8501
```

Test question:

```text
Can you recommend some triceps exercises that use a cable machine?
```

Expected behavior: the app returns cable-based triceps exercises from the
MegaGym dataset, such as cable triceps extensions or cable push-down variants,
and shows the retrieved context.

## 12. Copy Results Back To Your Laptop

Only do this if you intentionally want a local copy of the current HPC result
files. From your local laptop terminal, inside the repository root:

```bash
rsync -av \
  <USERNAME>@hpc-login.arnes.si:~/rag-app/report/results/ \
  report/results/
```

Expected result:

```text
baseline_vs_rag_examples.csv
baseline_vs_rag_examples.md
retrieval_eval_results.csv
retrieval_eval_results.md
```

## 13. Optional Batch Evaluation

After the manual setup has worked once, you can repeat the evaluation as a batch
job:

```bash
cd ~/rag-app
sbatch run_hpc_eval.slurm
```

Monitor:

```bash
squeue -u $USER
tail -f logs/eval-<JOBID>.out
tail -f logs/eval-<JOBID>.err
```