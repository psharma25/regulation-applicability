FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENV PORT=8000
# Defaults to the host's Ollama if you map it; otherwise runs deterministic.
ENV OLLAMA_URL=http://host.docker.internal:11434
CMD ["python", "app.py"]
