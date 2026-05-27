.PHONY: dev install setup test bot docker-build docker-up docker-down docker-logs

dev:
	./venv/bin/uvicorn agents.main:app --reload

install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

setup:
	./venv/bin/python agents/rag/setup.py

test:
	./venv/bin/python scripts/test_job.py $(JOB) $(DEVELOPER)

bot:
	./venv/bin/python scripts/telegram_bot.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api
