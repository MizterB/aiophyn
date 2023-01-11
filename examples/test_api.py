"""Run an example script to quickly test."""
import asyncio
import logging
from datetime import date

from aiohttp import ClientSession

from aiophyn import async_get_api
from aiophyn.errors import PhynError

_LOGGER = logging.getLogger()

USERNAME = "USERNAME_HERE"
PASSWORD = "PASSWORD_HERE"


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)
    async with ClientSession() as session:
        try:
            api = await async_get_api(USERNAME, PASSWORD, session=session)

            all_home_info = await api.home.get_homes(USERNAME)
            _LOGGER.info(all_home_info)

            home_info = all_home_info[0]
            _LOGGER.info(home_info)

            first_device_id = home_info["device_ids"][0]
            device_state = await api.device.get_state(first_device_id)
            _LOGGER.info(device_state)

            duration_today = date.today().strftime("%Y/%m/%d")
            consumption_info = await api.device.get_consumption(
                first_device_id, duration_today, details=True
            )
            _LOGGER.info(consumption_info)

            valve_status = device_state["sov_status"]["v"]
            _LOGGER.info(valve_status)

            # close_valve_response = await api.device.close_valve(first_device_id)
            # _LOGGER.info(close_valve_response)

            # open_valve_response = await api.device.open_valve(first_device_id)
            # _LOGGER.info(open_valve_response)

        except PhynError as err:
            _LOGGER.error("There was an error: %s", err)


asyncio.run(main())
