from drone import DroneInstance
from mavsdk import System
import asyncio


async def main() -> None:
    drone: DroneInstance = DroneInstance("0.0.0.0", 14540)

    while True:
        command = input("> ")
        match command:
            case "connect":
                await drone.connect()
            case "arm":
                await drone.arm()
            case "quit":
                break
            case _:
                print(f"Command '{command}' not found!")


if __name__ == "__main__":
    asyncio.run(main())
