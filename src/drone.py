import uuid
from mavsdk import System


class DroneInstance:
    __uuid: uuid.UUID
    __drone: System
    __host: str
    __port: int

    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__uuid = uuid.uuid1()
        self.__drone = System()
        pass

    def getUUID(self) -> uuid.UUID:
        return self.__uuid

    async def connect(self) -> bool:
        try:
            print(
                f"Connecting instance with uuid {str(self.__uuid)} to drone at {self.__host}:{self.__port}"
            )
            await self.__drone.connect(
                system_address=f"udpin://{self.__host}:{self.__port}"
            )
            return True
        except Exception as e:
            print(e)
            return False

    async def arm(self) -> bool:
        try:
            print(f"Arming drone with instance uuid {str(self.__uuid)}")
            await self.__drone.action.arm()
            return True
        except Exception as e:
            print(e)
            return False
