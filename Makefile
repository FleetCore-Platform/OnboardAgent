.PHONY: de format build run

de:
	@uv venv
	uv sync
	/bin/bash ./dev_env.sh

format:
	black .

run: format
	uv run -m src.main
