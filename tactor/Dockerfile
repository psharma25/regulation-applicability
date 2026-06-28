FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Set OLLAMA_HOST to a reachable Ollama instance, or leave unset to use the
# built-in heuristic backend (no external services required).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
