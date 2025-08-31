from loguru import logger

import dotenv
from awscrt import mqtt_request_response
from awsiot import iotjobs, mqtt5_client_builder
from awsiot.iotjobs import (
    GetPendingJobExecutionsResponse,
    DescribeJobExecutionResponse,
    JobExecutionSummary,
    JobExecutionData,
)
from pydantic import ValidationError

from src.Enums.job_status import JobStatus
from src.Models.job_document import Job


class IoTJobsClient:
    def __init__(
        self,
        cert_filepath: str,
        pri_key_filepath: str,
        thing_name: str,
        config_path: str = ".config.env",
    ):
        self.config: dict[str, str | None] = dotenv.dotenv_values(config_path)
        if not self.config.get("IOT_ENDPOINT") or not self.config.get("IOT_CLIENT_ID"):
            raise ValueError("Missing IOT_ENDPOINT or IOT_CLIENT_ID in config")

        self.thing_name = thing_name

        self.mqtt5_client = mqtt5_client_builder.mtls_from_path(
            endpoint=self.config["IOT_ENDPOINT"],
            cert_filepath=cert_filepath,
            pri_key_filepath=pri_key_filepath,
            clean_session=True,
            keep_alive_secs=30,
        )

        rr_options = mqtt_request_response.ClientOptions(
            max_request_response_subscriptions=2,
            max_streaming_subscriptions=2,
            operation_timeout_in_seconds=30,
        )

        self.jobs_client = iotjobs.IotJobsClientV2(self.mqtt5_client, rr_options)

    def connect(self):
        self.mqtt5_client.start()
        logger.info("Jobs client connected to MQTT broker")

    def get_pending_jobs(self) -> GetPendingJobExecutionsResponse:
        """Get list of pending job executions."""
        req = iotjobs.GetPendingJobExecutionsRequest(thing_name=self.thing_name)
        result: GetPendingJobExecutionsResponse = (
            self.jobs_client.get_pending_job_executions(req).result()
        )
        return result

    def get_next_in_progress_job(self) -> JobExecutionSummary | None:
        """Used when job execution was interrupted."""
        jobs = self.get_pending_jobs()
        if len(jobs.in_progress_jobs) != 0:
            return jobs.in_progress_jobs[0]
        return None

    def get_next_queued_job(self) -> JobExecutionSummary | None:
        """Get next job execution."""
        jobs = self.get_pending_jobs()
        if len(jobs.queued_jobs) != 0:
            return jobs.queued_jobs[0]
        return None

    @staticmethod
    def get_job_documents(
        job_describe_response: DescribeJobExecutionResponse,
    ) -> Job | None:
        """Get job documents."""
        job_data: JobExecutionData = job_describe_response.execution

        try:
            job_document: Job = Job.model_validate(job_data.job_document)
            return job_document
        except ValidationError as err:
            logger.warning("Unknown job document, cannot validate..")
            return None

    def describe_job_execution(self, job_id: str) -> DescribeJobExecutionResponse:
        """Get details of a specific job execution."""
        req = iotjobs.DescribeJobExecutionRequest(
            thing_name=self.thing_name, job_id=job_id
        )
        result: DescribeJobExecutionResponse = self.jobs_client.describe_job_execution(
            req
        ).result()
        logger.debug(f"Job {job_id} details: {result}")
        return result

    def update_job(self, job_id: str, status: JobStatus) -> None:
        req = iotjobs.UpdateJobExecutionRequest(
            thing_name=self.thing_name, job_id=job_id, status=status.value
        )
        result = self.jobs_client.update_job_execution(req).result()
        logger.debug(f"Updated job {job_id}: {result}")

    def disconnect(self) -> None:
        self.mqtt5_client.stop()
        logger.info("Disconnected jobs client")
