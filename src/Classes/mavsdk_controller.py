import asyncio
from functools import wraps
from typing import Callable

import cbor2
from mavsdk import System as MavSystem
from loguru import logger
from mavsdk.action import ActionError
from mavsdk.mission import MissionError
from mavsdk.mission_raw import MissionRawError
from src.Models.telemetry_data import (
    Battery as BatteryModel,
    Position as PositionModel,
    Health as HealthModel,
)
from rich.traceback import install

from src.Enums.connection_types import ConnectionType
from src.Models.telemetry_data import TelemetryData

install()


def ensure_connected(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.connected:
            logger.error("System not connected")
            exit(1)
        return await func(self, *args, **kwargs)

    return wrapper


class MavsdkController:
    def __init__(self, address: str, port: int, protocol: str) -> None:
        self.connected = False
        self.address: str = address
        self.port: int = port
        self.protocol: str = protocol
        self.system: MavSystem = MavSystem()

    async def connect(self) -> None:
        """Connect to drone hardware."""
        connection_string: str = (
            self.protocol
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
    async def upload_mission(
        self, path_to_mission: str, return_to_launch: bool = True
    ) -> None:
        """Upload a mission."""
        try:
            logger.info(f"Uploading mission {path_to_mission}")
            await self.system.mission.set_return_to_launch_after_mission(
                return_to_launch
            )

            out = await self.system.mission_raw.import_qgroundcontrol_mission(
                path_to_mission
            )

            logger.info(f"{len(out.mission_items)} mission items and")

            await self.system.mission_raw.upload_mission(out.mission_items)
            logger.info(f"Successfully uploaded mission")
        except Exception as e:
            logger.error(f"Failed to upload mission: {e}")

    @ensure_connected
    async def start_mission(self) -> None:
        try:
            await self.system.mission_raw.start_mission()
        except Exception as e:
            logger.error(f"Failed to start mission: {e}")

    @ensure_connected
    async def cancel_mission(self) -> None:
        try:
            logger.info("Canceling mission, returning to home.  .")
            await self.system.mission_raw.clear_mission()
            await self.system.action.return_to_launch()
        except Exception as e:
            logger.error(f"Failed to cancel mission: {e}")

    @ensure_connected
    async def subscribe_mission_finished(self, callback: Callable) -> None:
        try:
            logger.info(f"Subscribing to mission completed!")
            async for progress in self.system.mission_raw.mission_progress():
                if progress.current == progress.total:
                    logger.info("Finishing mission. Landing drone...")
                    break

            async for in_air in self.system.telemetry.in_air():
                if not in_air:
                    break

            callback()
        except Exception as e:
            logger.error(f"Error while waiting for mission process: {e}")

    @ensure_connected
    async def get_telemetry(self) -> TelemetryData:
        """
        Fetches the drone's telemetry data to TelemetryData object.
        Returns:
            TelemetryData: A TelemetryData object containing the telemetry data.
        """
        position_raw, battery_raw, health_raw, in_air = await asyncio.gather(
            self.system.telemetry.position().__anext__(),
            self.system.telemetry.battery().__anext__(),
            self.system.telemetry.health().__anext__(),
            self.system.telemetry.in_air().__anext__(),
        )

        position = PositionModel(**position_raw.__dict__)
        battery = BatteryModel(**battery_raw.__dict__)
        health = HealthModel(**health_raw.__dict__)

        return TelemetryData(
            position=position, battery=battery, health=health, in_air=in_air
        )

    @ensure_connected
    async def get_telemetry_json(self) -> str:
        """
        Fetches the drone's telemetry data into serialized json.
        Returns:
            str: The json representation of a TelemetryData object.
        """

        telemetry: TelemetryData = await self.get_telemetry()
        return telemetry.model_dump_json()

    @ensure_connected
    async def get_telemetry_cbor(self) -> bytes:
        """
        Fetches the drone's telemetry data to a CBOR serialized object.
        Returns:
            bytes: The bytes of a CBOR serialized TelemetryData object containing the telemetry.
        """
        telemetry: TelemetryData = await self.get_telemetry()

        return cbor2.dumps(telemetry.model_dump())
