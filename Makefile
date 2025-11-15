.PHONY: de format build run

default: run

de:
ifeq ($(gazebo),1)
	@uv venv
	uv sync
	/bin/bash ./sim/gazebo_dev_env.sh
else ifeq ($(pegasus),1)
	@uv venv
	uv sync
	/bin/bash ./sim/pegasus_dev_env.sh
else
	@uv venv
	uv sync
	/bin/bash ./sim/gazebo_classic_dev_env.sh
endif

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