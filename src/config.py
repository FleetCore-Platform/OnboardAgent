import os.path

from dotenv import dotenv_values

from src.enums.connection_types import ConnectionTypes
from src.exceptions.config_exceptions import ConfigValueException, ConfigTypeException


class Config:
    def __init__(self, config_file=".config.env"):
        raw = dotenv_values(config_file)

        self.endpoint: str = self._require(raw, "IOT_ENDPOINT")
        self.thing_name: str = self._require(raw, "IOT_THING_NAME")
        self.drone_address: str = self._require(raw, "DRONE_ADDRESS")
        self.drone_port: int = self._require_int(raw, "DRONE_PORT")
        self.drone_connection_type: ConnectionTypes = self._require_enum(
            raw, "DRONE_CONNECTION_TYPE", ConnectionTypes
        )
        self.cert_filepath: str = self._require_path(raw, "CERT_FILEPATH")
        self.pri_key_filepath: str = self._require_path(raw, "PRIVATE_KEY_FILEPATH")
        self.ca_filepath: str = self._require_path(raw, "CA_FILEPATH")
        self.internal_topic = f"$aws/things/{self.thing_name}/jobs/notify"
        self.cancel_topic = f"groups/{self.thing_name}/cancel"
        self.telemetry_topic = f"devices/{self.thing_name}/telemetry"

    def _require(self, config: dict, key: str) -> str:
        value = config.get(key)
        if value is None:
            raise ConfigValueException(f"{key} not set")
        return value

    def _require_path(self, config: dict, key: str) -> str:
        value = self._require(config, key)

        if os.path.exists(value) and os.path.isfile(value):
            return value
        else:
            raise ConfigTypeException(f"{key} not a file")

    def _require_int(self, config: dict, key: str) -> int:
        value = self._require(config, key)
        try:
            return int(value)
        except ValueError:
            raise ConfigTypeException(f"{key} must be integer")

    def _require_enum(self, config: dict, key: str, enum_type):
        value = self._require(config, key)
        try:
            return enum_type(value)
        except ValueError:
            raise ConfigTypeException(f"{key} must be valid {enum_type.__name__}")
