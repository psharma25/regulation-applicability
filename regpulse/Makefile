.PHONY: dev test seed up up-ai down models fmt

dev:            ## run locally on SQLite (no docker), $0 inference
	cd backend && DATABASE_URL=sqlite:///./regpulse.db USE_LLM=false \
	  uvicorn app.main:app --reload --port 8000

test:           ## run the test suite
	cd backend && python -m pytest -q

seed:           ## rebuild seed datasets from scripts/build_seed.py
	python scripts/build_seed.py

up:             ## run full stack (Postgres + API), templates only ($0)
	docker compose up --build

up-ai:          ## run full stack WITH local Ollama LLM + embeddings
	docker compose --profile ai up --build -d
	./scripts/pull_models.sh

down:
	docker compose down

models:         ## pull local open-source models into the ollama service
	./scripts/pull_models.sh
