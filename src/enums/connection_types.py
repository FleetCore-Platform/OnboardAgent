from enum import Enum


class ConnectionTypes(Enum):
    SERIAL = 0,
    UDP = 1,
    TCP = 2,