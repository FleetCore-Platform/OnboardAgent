#!/bin/bash

run() {
  docker run -it --privileged \
	  --env=LOCAL_USER_ID="1000" \
	  -v ./PX4-Autopilot:/src/PX4-Autopilot/:rw \
	  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
	  -e DISPLAY=:1 \
	  --network host \
	  --name=px4-sim \
	  px4io/px4-dev-simulation-focal:latest \
	  bash -c "cd /src/PX4-Autopilot && make px4_sitl gazebo-classic; exec bash"

  docker container remove px4-sim
}

if [ -d "./PX4-Autopilot" ]; then
	echo "PX4 Autopilot already present, starting development environment..."
	run
else
	echo "PX4 Autopilot cannot be found locally, cloning.."
	git clone --recursive https://github.com/PX4/PX4-Autopilot.git PX4-Autopilot
	run
fi
