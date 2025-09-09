import asyncio
import base64
import time

import cbor2
from loguru import logger
from pathlib import Path

import dotenv

from src.Classes.mavsdk_controller import MavsdkController
from src.Models.telemetry_data import TelemetryData, Battery, Position, Health
from src.utils.download_handler import handle_download

from awsiot.iotjobs import JobExecutionSummary

from src.Classes.mqtt_base import IoTBaseClient
from src.Classes.mqtt_jobs import IoTJobsClient
from awscrt import io

from rich.traceback import install

from src.Enums.job_status import JobStatus
from src.Models.job_document import Job
from src.utils.zip_manager import extract_mission

# DEBUG
# io.init_logging(io.LogLevel.Trace, "stderr")
# DEBUG

install()

config: dict[str, str | None] = dotenv.dotenv_values(".config.env")
thing_name: str = config["IOT_THING_NAME"]

internal_topic = f"$aws/things/{thing_name}/jobs/notify"
cancel_topic = f"groups/{thing_name}/cancel"
telemetry_topic = f"devices/{thing_name}/telemetry"

in_execution = False

system: MavsdkController = MavsdkController(
    config["DRONE_ADDRESS"], int(config["DRONE_PORT"]), config["DRONE_CONNECTION_TYPE"]
)

loop = None


def job_handler(topic, payload, **_):
    async def drone_executor():
        await system.connect()
        await system.upload_mission(mission_plan_file, return_to_launch=True)

        await system.arm()
        await system.start_mission()

        await system.subscribe_mission_finished(handle_mission_end)

    def handle_mission_end():
        jobs_client.update_job(next_job_id, JobStatus.SUCCEEDED)

        global in_execution
        in_execution = False

    next_queued_job: JobExecutionSummary = jobs_client.get_next_queued_job()
    if not next_queued_job:
        logger.debug("No next queued job")
        return

    next_job_id: str = next_queued_job.job_id

    global in_execution
    if in_execution:
        logger.warning(
            f"Job already in action, rejecting next job with ID {next_job_id}"
        )
        jobs_client.update_job(next_job_id, JobStatus.REJECTED)
        return
    else:
        in_execution = True

    job_description = jobs_client.describe_job_execution(next_job_id)
    document: Job | None = jobs_client.get_job_documents(job_description)

    if document and document.steps[0].action.name == "Download-File":

        status: int
        path: str
        status, path = handle_download(
            document.steps[0].action.input.args[0],
            document.steps[0].action.input.args[1],
        )

        if status == 0:
            logger.info("Download succeeded..")

            mission_plan_file: str = extract_mission(
                path, thing_name, document.steps[0].action.input.args[1]
            )

            asyncio.run_coroutine_threadsafe(drone_executor(), loop)
            return
        else:
            logger.warning("Download failed, cancelling execution..")
            jobs_client.update_job(next_job_id, JobStatus.FAILED)
            in_execution = False

            return

    else:
        logger.warning(
            f"Unknown or invalid job document in job {next_job_id}, rejecting..."
        )
        jobs_client.update_job(next_job_id, JobStatus.REJECTED)
        in_execution = False

        return


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    certs = base_dir.parent / "certs"

    jobs_client = IoTJobsClient(
        cert_filepath=str(certs / "test1.cert.pem"),
        pri_key_filepath=str(certs / "test1.private.key"),
        thing_name=thing_name,
    )

    basic_client = IoTBaseClient(
        cert_filepath=str(certs / "test1.cert.pem"),
        pri_key_filepath=str(certs / "test1.private.key"),
        ca_filepath=str(certs / "root-CA.crt"),
    )

    jobs_client.connect()
    basic_client.connect()

    # basic_client.subscribe(internal_topic, job_handler)

    # TODO: Implement cancel job logic
    # basic_client.subscribe(cancel_topic)

    # basic_client.subscribe(
    #     f"devices/{thing_name}/messages",
    #     callback=lambda topic, payload, **_: print(payload),
    # )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            loop.run_until_complete(asyncio.sleep(1))

    except (KeyboardInterrupt, InterruptedError):
        logger.info("Stopping")
    except Exception as e:
        logger.error(e)
    finally:
        loop.close()
        jobs_client.disconnect()
        basic_client.disconnect()
