.PHONY: de format build run

default: run

de:
	@uv venv
	uv sync
	/bin/bash ./dev_env.sh

format:
	black .

run: format
	uv run -m src.main

test:
ifeq ($(all),1)
	uv run pytest tests/
else
	uv run pytest tests/unit/
endif