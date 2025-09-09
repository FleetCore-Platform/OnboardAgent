import json
from loguru import logger

import dotenv
from awscrt import mqtt
from awsiot import mqtt_connection_builder


class IoTBaseClient:
    def __init__(
        self,
        cert_filepath: str,
        pri_key_filepath: str,
        ca_filepath: str,
        config_path: str = ".config.env",
    ):
        self.config: dict[str, str | None] = dotenv.dotenv_values(config_path)
        if not self.config.get("IOT_ENDPOINT") or not self.config.get("IOT_CLIENT_ID"):
            raise ValueError("Missing IOT_ENDPOINT or IOT_CLIENT_ID in config")

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            cert_filepath=cert_filepath,
            pri_key_filepath=pri_key_filepath,
            ca_filepath=ca_filepath,
            endpoint=self.config["IOT_ENDPOINT"],
            client_id=self.config["IOT_CLIENT_ID"],
            clean_session=False,
            keep_alive_secs=30,
        )

    def connect(self):
        future = self.mqtt_connection.connect()
        future.result()
        logger.info("Basic MQTT client connected")

    def subscribe(self, topic: str, callback):
        future, _ = self.mqtt_connection.subscribe(
            topic=topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=callback
        )
        future.result()
        logger.info(f"Subscribed to {topic}")

    def unsubscribe(self, topic: str):
        future, _ = self.mqtt_connection.unsubscribe(topic=topic)
        future.result()
        logger.info(f"Unsubscribed from {topic}")

    def publish(self, topic: str, message: str):
        self.mqtt_connection.publish(
            topic=topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE
        )
        logger.debug(f"Published to {topic}: {message}")

    def disconnect(self):
        future = self.mqtt_connection.disconnect()
        future.result()
        logger.info("Disconnected basic client")
