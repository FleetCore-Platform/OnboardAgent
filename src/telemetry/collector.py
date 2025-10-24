import asyncio

from src.models.telemetry_data import TelemetryData
from src.models.telemetry_data import (
    Battery as BatteryModel,
    Position as PositionModel,
    Health as HealthModel,
)


class TelemetryCollector:
    async def get_telemetry(self) -> TelemetryData:
        """
        Fetches the drone's telemetry data to TelemetryData object.
        Returns:
            TelemetryData: A TelemetryData object containing the telemetry data.
        """
        position_raw, battery_raw, health_raw, in_air = await asyncio.gather(
            self.__system.telemetry.position().__anext__(),
            self.__system.telemetry.battery().__anext__(),
            self.__system.telemetry.health().__anext__(),
            self.__system.telemetry.in_air().__anext__(),
        )

        position = PositionModel(**position_raw.__dict__)
        battery = BatteryModel(**battery_raw.__dict__)
        health = HealthModel(**health_raw.__dict__)

        return TelemetryData(
            position=position, battery=battery, health=health, in_air=in_air
        )

    async def get_telemetry_json(self) -> str:
        """
        Fetches the drone's telemetry data into serialized json.
        Returns:
            str: The json representation of a TelemetryData object.
        """

        telemetry: TelemetryData = await self.get_telemetry()
        return telemetry.model_dump_json()

    async def get_telemetry_cbor(self) -> str:
        """
        Fetches the drone's telemetry data to a CBOR serialized object.
        Returns:
            str: Base64 ascii string of the CBOR serialized TelemetryData object containing the telemetry.
        """
        telemetry: TelemetryData = await self.get_telemetry()

        cbor_bytes: bytes = cbor2.dumps(telemetry.model_dump())
        encoded = base64.b64encode(cbor_bytes).decode("ascii")
        return encoded
