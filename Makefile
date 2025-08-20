.PHONY: de format build run

de:
	/bin/bash ./dev_env.sh

format:
	black .

run:
	uv run src/main.py
