#!/bin/bash

setup() {
	docker build -t fleetcoreagent/px4-dev-gazeboo-harmonic:latest -f ./sim/Dockerfile.PX4 ./sim
}

run() {
  xhost +local:docker

	docker run -it --privileged \
    --env=LOCAL_USER_ID='1000' \
		-v ./sim/PX4-Autopilot:/src/PX4-Autopilot/:rw \
		-v /tmp/.X11-unix:/tmp/.X11-unix:ro \
		-e DISPLAY="$DISPLAY" \
		-e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    --device=/dev/dri:/dev/dri \
    --gpus all \
		--network host \
		--name=px4-sim \
		fleetcoreagent/px4-dev-gazeboo-harmonic:latest \
		bash -c "cd /src/PX4-Autopilot && make px4_sitl gz_x500_mono_cam; exec bash"

	docker container remove px4-sim
}

if ! command -v nvidia-smi; then
  echo "No Nvidia GPU detected, exiting.."
  exit 1
fi

if [ ! -d "./sim/PX4-Autopilot" ]; then
	echo "PX4 Autopilot cannot be found locally, cloning.."
	git clone --recursive https://github.com/PX4/PX4-Autopilot.git PX4-Autopilot
	setup
	run
elif [ -z "$(docker images -q fleetcoreagent/px4-dev-gazeboo-harmonic:latest)" ]; then
	echo "Image not found, building..."
	setup
	run
else
	echo "PX4 Autopilot already present, starting development environment..."
	run
fi