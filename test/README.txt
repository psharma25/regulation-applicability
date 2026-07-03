# LLM + RAG with human approval — self-contained in GitHub Codespaces

A minimal, fully self-contained experiment:

- **LLM**: a small pretrained open model (Llama 3.2 1B) served locally by Ollama — no API keys, no external calls
- **RAG**: your documents in `docs/` are chunked, embedded (sentence-transformers), and retrieved by cosine similarity
- **Web UI**: one page with an **Ask** tab and a **Review queue** tab
- **Human approval**: every answer waits in a queue until a human approves, edits, or rejects it — the asker never sees an unapproved answer

Everything runs inside one GitHub Codespace (free tier works).

## Step-by-step

### 1. Put this project on GitHub
1. Go to https://github.com/new and create a repository (e.g. `llm-rag-approval`, private is fine).
2. Upload this folder's contents: on the new repo page click **uploading an existing file**, drag the whole folder in, and commit.
   (Or from a terminal: `git init && git add -A && git commit -m "init" && git remote add origin <your-repo-url> && git push -u origin main`)

### 2. Open a Codespace
1. On your repo page click the green **Code** button → **Codespaces** tab → **Create codespace on main**.
2. Wait ~3–5 minutes. The `.devcontainer` config automatically installs Python dependencies and Ollama. Watch the terminal at the bottom; it finishes with "Setup complete."

### 3. Start the app
In the Codespaces terminal:

```bash
./start.sh
```

First run pulls the model (~1.3 GB, a couple of minutes). When you see `Uvicorn running on 0.0.0.0:8000`, a preview pane opens automatically — or click the **Ports** tab, find port 8000, and click the globe icon to open it in a browser tab.

### 4. Use it
1. **Ask tab** — type a question about the sample docs, e.g. *"What does the security policy say about MFA?"* You'll see: generating → waiting for human approval.
2. **Review queue tab** — the draft appears with its retrieved sources and similarity scores. Edit the text if you like, then **Approve** (or **Reject**).
3. Back on the **Ask tab**, the approved answer appears with its sources.

Self-approval mode is the same flow with one person: you ask, then switch tabs and approve your own draft. For a two-person demo, send a teammate the same URL (make the port public in the Ports tab) — one person asks, the other reviews.

### 5. "Train" the RAG on your own documents
1. Drop your `.md`, `.txt`, or `.pdf` files into the `docs/` folder (delete the samples if you want).
2. Click **Rebuild RAG index** in the Review tab (or restart the app).
3. Ask questions about your content.

There's no gradient training here — "training" a RAG system means building the embedding index. That's why it's fast and repeatable.

## How it works (2-minute tour)

```
docs/*.md,pdf ──chunk──> embeddings (MiniLM) ──┐
                                               v
Ask tab ──/api/ask──> retrieve top-4 chunks ──> prompt ──> Ollama (Llama 3.2 1B)
                                                              │ draft
                                                              v
                                        Review queue (human approves/edits/rejects)
                                                              │
Ask tab <──/api/status poll── approved answer + sources ◄─────┘
```

- `app/rag.py` — chunking, embedding, retrieval (~80 lines)
- `app/main.py` — API + approval state machine (~150 lines)
- `static/index.html` — the whole UI (no framework)

## Tweaks

| Want | How |
|---|---|
| Faster answers | `export OLLAMA_MODEL=qwen2.5:0.5b` before `./start.sh` |
| Better answers | `export OLLAMA_MODEL=llama3.2:3b` (needs the 4-core Codespace) |
| Bigger/smaller chunks | `CHUNK_SIZE` in `app/rag.py` |
| More context per answer | `k` in `rag.retrieve()` |
| Audit log of approvals | persist `ANSWERS` to a JSON file in `app/main.py` |

## Notes and limits

- State is in memory — restarting the app clears the queue. Fine for an experiment.
- A 1B model on CPU is modest: expect 10–30 s per answer and occasional wrong-but-confident drafts. That's exactly what makes the human-approval step feel real.
- Codespaces free tier includes 120 core-hours/month; a 4-core machine gives you ~30 hours. **Stop the Codespace when done** (Code → Codespaces → Stop).
