import time
from loguru import logger
from pathlib import Path

import dotenv

from src.utils.download_handler import handle_download

from awsiot.iotjobs import JobExecutionSummary

from src.Classes.mqtt_base import IoTBaseClient
from src.Classes.mqtt_jobs import IoTJobsClient
from awscrt import io

from rich.traceback import install

from src.Enums.job_status import JobStatus
from src.Models.job_document import Job

# DEBUG
# io.init_logging(io.LogLevel.Trace, "stderr")
# DEBUG

install()

config: dict[str, str | None] = dotenv.dotenv_values(".config.env")
thing_name: str = config["IOT_THING_NAME"]

internal_topic = f"$aws/things/{thing_name}/jobs/notify"


def job_handler(topic, payload, **_):
    next_queued_job: JobExecutionSummary = jobs_client.get_next_queued_job()
    if not next_queued_job:
        logger.debug("No next queued job")
        return

    next_job_id: str = next_queued_job.job_id
    job_description = jobs_client.describe_job_execution(next_job_id)
    document: Job | None = jobs_client.get_job_documents(job_description)

    if document and document.steps[0].action.name == "Download-File":

        status: int = handle_download(
            document.steps[0].action.input.args[0],
            document.steps[0].action.input.args[1],
        )

        if status == 0:
            logger.info("Download succeeded..")
            jobs_client.update_job(next_job_id, JobStatus.SUCCEEDED)
        else:
            logger.warning("Download failed, cancelling execution..")
            jobs_client.update_job(next_job_id, JobStatus.FAILED)

    else:
        logger.warning(
            f"Unknown or invalid job document in job {next_job_id}, rejecting..."
        )
        jobs_client.update_job(next_job_id, JobStatus.REJECTED)


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

    basic_client.subscribe(internal_topic, job_handler)

    try:
        while True:
            time.sleep(0)
    except (KeyboardInterrupt, InterruptedError):
        logger.info("Stopping")
    except Exception as e:
        logger.error(e)
    finally:
        jobs_client.disconnect()
        basic_client.disconnect()
