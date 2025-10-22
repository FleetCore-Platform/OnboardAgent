from typing import Any

from pydantic import BaseModel


class Position(BaseModel):
    latitude_deg: float
    longitude_deg: float
    absolute_altitude_m: float
    relative_altitude_m: float


class Battery(BaseModel):
    temperature_degc: float
    voltage_v: float
    current_battery_a: float
    capacity_consumed_ah: float
    remaining_percent: float


class Health(BaseModel):
    is_gyrometer_calibration_ok: bool
    is_accelerometer_calibration_ok: bool
    is_magnetometer_calibration_ok: bool
    is_local_position_ok: bool
    is_global_position_ok: bool
    is_home_position_ok: bool
    is_armable: bool


class TelemetryData(BaseModel):
    position: Position
    battery: Battery
    health: Health
    in_air: bool
