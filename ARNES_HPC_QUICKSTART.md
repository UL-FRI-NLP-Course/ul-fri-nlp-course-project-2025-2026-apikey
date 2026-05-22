# Arnes HPC Quickstart

This is a guide to running the project on Arnes HPC.

You will:

- upload the repository to HPC
- prepare Python and Ollama
- request a GPU node
- build the Qdrant index
- run evaluation
- open the Streamlit app through an SSH tunnel

This guide assumes a Bash/Linux shell for the commands below.

If you are on Windows and do not already have a Linux-like shell, use WSL,
Git Bash, or a similar Unix-like environment for the upload commands.

Replace `<USERNAME>` with your Arnes username.

## 1. Before you start

You should already have the repository on your laptop.

This guide uses:

- project folder on HPC: `~/rag-app`
- model: `llama3.2:1b`
- local Qdrant storage: `~/rag-app/qdrant_storage`

Important:

- use the login node only for setup and SLURM commands
- run Ollama, indexing, evaluation, and Streamlit only on a GPU compute node

## 2. One-time SSH and OTP setup

If you already tested SSH login to Arnes HPC before, you can skip this section.

Check whether you already have an SSH public key:

```bash
test -f ~/.ssh/id_ed25519.pub && echo "SSH public key exists" || echo "No default SSH public key"
```

If not, create one:

```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Copy the public key and add it at:

```text
https://fido.sling.si/
```

The key should be added under your profile in `SSH public keys`.

Important: if your key has a custom name such as `id_ed25519_sling`, use that
exact filename in the SSH commands below instead of `id_ed25519`.

Then configure the OTP token:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-otp.arnes.si
```

Scan the QR code with Google Authenticator or a similar app, then enter the generated OTP code to verify.

After that, test normal login:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
```

If it works, you should see the login prompt on the HPC login node.

## 3. Upload the project to HPC

From your laptop, inside the repository root.

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

If `rsync` fails with `Permission denied (publickey)`, the quickstart is not
necessarily wrong. It usually means the SSH key used by `rsync` is not the same
key that works for your manual `ssh` login. In that case, first verify which key
works with a normal SSH command, for example:

```bash
ssh -i ~/.ssh/id_ed25519_sling -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
```

Then either configure SSH to use that key by default for Arnes HPC, or run the
upload from an environment where that key is already configured.

Then log in:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes <USERNAME>@hpc-login.arnes.si
cd ~/rag-app
ls -la
```

If you use a custom key name, replace `id_ed25519` here as well.

Success looks like this:

- you are inside `~/rag-app`
- you can see files such as `app.py`, `requirements.txt`, `src/`, `scripts/`, and `report/`

## 4. Create the Python environment

This is usually needed only once per HPC copy of the project.

```bash
cd ~/rag-app
mkdir -p ~/rag-app ~/models/ollama ~/.local ~/logs
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Success looks like this:

- the `.venv` folder exists
- `pip install -r requirements.txt` finishes without errors

## 5. Install Ollama

Run this on the login node:

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

The warning about not connecting to a running Ollama instance is normal here.

To keep these variables for future sessions, add them to `.bashrc`:

```bash
grep -q 'OLLAMA_MODELS' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export PATH="$HOME/.local/bin:$PATH"
export OLLAMA_MODELS="$HOME/models/ollama"
EOF
```

## 6. Request a GPU node

From the login node:

```bash
salloc --partition=gpu --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=02:00:00
srun --pty bash
```

Check that you are really on a GPU node:

```bash
hostname
nvidia-smi
```

Success looks like this:

- hostname starts with something like `wn...`
- `nvidia-smi` shows a GPU such as `Tesla V100S-PCIE-32GB`

## 7. Start Ollama and pull the model

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

If Ollama is running correctly, you should get a JSON response.

Now pull the model:

```bash
ollama pull llama3.2:1b
ollama list
```

Optional quick test:

```bash
ollama run llama3.2:1b "Answer in one sentence: what is a dumbbell chest press?"
ollama ps
```

Success looks like this:

- `llama3.2:1b` appears in `ollama list`
- `ollama ps` shows the model using the GPU

## 8. Build the vector index

Still on the GPU node:

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
python scripts/index_megagym.py
```

Expected result:

```text
Indexed 2918 exercises.
```

## 9. Run evaluation

### Retrieval only

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
python scripts/run_evaluation.py --mode retrieval
```

Expected result from the verified run:

```text
Evaluated 11 retrieval queries
Hit@1: 0.636
Hit@3: 0.909
Hit@5: 0.909
Precision@5: 0.582
MRR: 0.742
```

### Baseline vs RAG comparison

```bash
cd ~/rag-app
source .venv/bin/activate
export QDRANT_PATH="$HOME/rag-app/qdrant_storage"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="llama3.2:1b"
python scripts/run_evaluation.py --mode comparison
```

### Run both in one command

```bash
python scripts/run_evaluation.py
```

Output files are written to:

```text
report/results/
```

## 10. Run the Streamlit app

Keep Ollama running on the GPU node, then start Streamlit:

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

Find the compute node name:

```bash
hostname
```

Example:

```text
wn203.arnes.si
```

From a new terminal on your laptop, open the SSH tunnel:

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  -L 8501:wn203:8501 \
  <USERNAME>@hpc-login.arnes.si
```

Then open this in your browser:

```text
http://127.0.0.1:8501
```

## 11. Copy results back to your laptop

Only do this if you want a local copy of the HPC-generated result files.

From your laptop, inside the repository root:

```bash
rsync -av \
  <USERNAME>@hpc-login.arnes.si:~/rag-app/report/results/ \
  report/results/
```

## 12. What success looks like

The HPC path is working correctly when:

- you can log in with SSH and OTP
- you can get a GPU node with `salloc` and `srun`
- `llama3.2:1b` runs through Ollama on the GPU node
- indexing finishes with `Indexed 2918 exercises.`
- evaluation writes files into `report/results/`
- Streamlit opens through the SSH tunnel and answers questions

## 13. Optional batch evaluation

After the manual path works once, you can run evaluation as a batch job:

```bash
cd ~/rag-app
sbatch run_hpc_eval.slurm
```

Monitor it with:

```bash
squeue -u $USER
tail -f logs/eval-<JOBID>.out
tail -f logs/eval-<JOBID>.err
```