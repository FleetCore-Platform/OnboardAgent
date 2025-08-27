from enum import Enum


class ConnectionType(Enum):
    UDPIN = "udpin"
    UDPOUT = "udpout"
    TCPIN = "tcpin"
    TCPOUT = "tcpout"
    SERIAL = "serial"
