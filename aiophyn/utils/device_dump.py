import asyncio
import logging
from pprint import pprint

from aiohttp import ClientSession

from aiophyn import async_get_api
from aiophyn.errors import PhynError

_LOGGER = logging.getLogger()


async def device_dump(username: str, password: str) -> None:
    device_states = []
    away_mode_states = []
    async with ClientSession() as session:
        try:
            api = await async_get_api(username, password, session=session)
            all_homes = await api.home.get_homes(username)
            for home in all_homes:
                for device_id in home.get("device_ids", []):
                    device_state = await api.device.get_state(device_id)
                    device_states.append(device_state)

                    away_mode = await api.device.get_away_mode(device_id)
                    away_mode_states.append(away_mode)
            print("\n" * 3)
            pprint(device_states)
            print("\n" * 3)
            pprint(away_mode_states)
            print("\n" * 3)

        except PhynError as err:
            _LOGGER.error("There was an error: %s", err)


async def main() -> None:
    username = input("Username: ")
    password = input("Password: ")
    await device_dump(username, password)


asyncio.run(main())
