import asyncio
from functools import wraps

from mavsdk import System as MavSystem
from loguru import logger
from mavsdk.action import ActionError
from mavsdk.mission_raw import MissionRawError

from src.Enums.connection_types import ConnectionType


def ensure_connected(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.connected:
            logger.error("System not connected")
            exit(1)
        return await func(self, *args, **kwargs)

    return wrapper


class MavsdkController:
    def __init__(self, address: str, port: int, protocol: ConnectionType) -> None:
        self.connected = False
        self.address: str = address
        self.port: int = port
        self.protocol: ConnectionType = protocol
        self.system: MavSystem = MavSystem()

    async def connect(self) -> None:
        """Connect to drone hardware."""
        connection_string: str = (
            self.protocol.value
            + (":///" if self.protocol == ConnectionType.SERIAL else "://")
            + self.address
            + ":"
            + str(self.port)
        )

        try:
            logger.info(f"Connecting to {connection_string}")
            await self.system.connect(system_address=connection_string)

            async for state in self.system.core.connection_state():
                if state.is_connected:
                    break

            self.connected = True
            logger.info(f"Connected to {connection_string}")
        except Exception as e:
            logger.error(f"Failed to connect to mavsdk on {connection_string}: {e}")

    @ensure_connected
    async def arm(self) -> None:
        """Arm the drone."""
        try:
            await self.system.action.arm()
            logger.info(f"Successfully armed the drone")
        except ActionError as e:
            logger.error(f"Failed to arm the drone: {e}")

    @ensure_connected
    async def upload_mission(self, path_to_mission: str) -> None:
        """Upload a mission."""
        try:
            out = await self.system.mission_raw.import_qgroundcontrol_mission(
                path_to_mission
            )

            logger.info(f"{len(out.mission_items)} mission items and")

            await self.system.mission_raw.upload_mission(out.mission_items)
            logger.info(f"Successfully uploaded mission")
        except MissionRawError | FileNotFoundError as e:
            logger.error(f"Failed to upload mission: {e}")


async def main():
    mavsdk_controller = MavsdkController("0.0.0.0", 14540, ConnectionType.UDPIN)

    await mavsdk_controller.connect()
    await mavsdk_controller.arm()


if __name__ == "__main__":
    asyncio.run(main())
