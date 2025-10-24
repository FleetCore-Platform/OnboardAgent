import unittest
from unittest.mock import patch
from src.config import Config
from src.enums.connection_types import ConnectionTypes
from src.exceptions.config_exceptions import ConfigValueException, ConfigTypeException


class ConfigTest(unittest.TestCase):

    @patch("src.config.dotenv_values")
    def test_config_load_success(self, mock_dotenv):
        mock_dotenv.return_value = {
            "IOT_ENDPOINT": "test.iot.aws.com",
            "IOT_THING_NAME": "drone1",
            "DRONE_ADDRESS": "127.0.0.1",
            "DRONE_PORT": "14540",
            "DRONE_CONNECTION_TYPE": "udpin",
            "CERT_FILEPATH": "/certs/cert.pem",
            "PRIVATE_KEY_FILEPATH": "/certs/key.pem",
            "CA_FILEPATH": "/certs/ca.pem",
        }

        config = Config()

        assert config.endpoint == "test.iot.aws.com"
        assert config.thing_name == "drone1"
        assert config.drone_address == "127.0.0.1"
        assert config.drone_port == 14540
        assert config.drone_connection_type == ConnectionTypes.UDPIN
        assert config.internal_topic == "$aws/things/drone1/jobs/notify"

    @patch("src.config.dotenv_values")
    def test_missing_required_field(self, mock_dotenv):
        mock_dotenv.return_value = {"IOT_ENDPOINT": "test.iot.aws.com"}

        with self.assertRaises(ConfigValueException) as ctx:
            Config()

        assert "IOT_THING_NAME" in str(ctx.exception)

    @patch("src.config.dotenv_values")
    def test_invalid_port_type(self, mock_dotenv):
        mock_dotenv.return_value = {
            "IOT_ENDPOINT": "test.iot.aws.com",
            "IOT_THING_NAME": "drone1",
            "DRONE_ADDRESS": "127.0.0.1",
            "DRONE_PORT": "invalid",
            "DRONE_CONNECTION_TYPE": "udpin",
            "CERT_FILEPATH": "/certs/cert.pem",
            "PRIVATE_KEY_FILEPATH": "/certs/key.pem",
            "CA_FILEPATH": "/certs/ca.pem",
        }

        with self.assertRaises(ConfigTypeException) as ctx:
            Config()

        assert "must be integer" in str(ctx.exception)

    @patch("src.config.dotenv_values")
    def test_invalid_connection_type(self, mock_dotenv):
        mock_dotenv.return_value = {
            "IOT_ENDPOINT": "test.iot.aws.com",
            "IOT_THING_NAME": "drone1",
            "DRONE_ADDRESS": "127.0.0.1",
            "DRONE_PORT": "14540",
            "DRONE_CONNECTION_TYPE": "invalid_type",
            "CERT_FILEPATH": "/certs/cert.pem",
            "PRIVATE_KEY_FILEPATH": "/certs/key.pem",
            "CA_FILEPATH": "/certs/ca.pem",
        }

        with self.assertRaises(ConfigTypeException) as ctx:
            Config()

        assert "ConnectionTypes" in str(ctx.exception)
