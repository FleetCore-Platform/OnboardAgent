from enum import Enum


class JobStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    QUEUED = "QUEUED"
    TIMED_OUT = "TIMED_OUT"
