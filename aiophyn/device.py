"""Define /devices endpoints."""
from typing import Awaitable, Callable, Optional

from .const import API_BASE


class Device:
    """Define an object to handle the endpoints."""

    def __init__(self, request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._request: Callable[..., Awaitable] = request

    async def get_state(self, device_id: str) -> dict:
        """Return state of a device.

        :param device_id: Unique identifier for the device
        :type device_id: ``str``
        :rtype: ``dict``
        """
        return await self._request("get", f"{API_BASE}/devices/{device_id}/state")

    async def get_consumption(
        self,
        device_id: str,
        duration: str,
        precision: int = 6,
        details: Optional[str] = False,
        event_count: Optional[str] = False,
        comparison: Optional[str] = False,
    ) -> dict:
        """Return water consumption of a device.

        :param device_id: Unique identifier for the device
        :type device_id: ``str``
        :param duration: Date string formatted as 'YYYY/MM/DD', 'YYYY/MM', or 'YYYY'
        :type duration: ``str``
        :param precision: Decimal places of measurement precision
        :type precision: ``int``
        :param details: Include detailed breakdown of consumption
        :type details: ``bool``
        :param event_count: Include the event count
        :type event_count: ``bool``
        :param comparison: Include comparison data
        :type comparison: ``bool``
        :rtype: ``dict``
        """

        params = {
            "device_id": device_id,
            "duration": duration,
            "precision": precision,
        }

        if details:
            params["details"] = "Y"

        if event_count:
            params["event_count"] = "Y"

        if comparison:
            params["comparison"] = "Y"

        return await self._request(
            "get", f"{API_BASE}/devices/{device_id}/consumption/details", params=params
        )

    async def open_valve(self, device_id: str) -> None:
        """Open a device shutoff valve.

        :param device_id: Unique identifier for the device
        :type device_id: ``str``
        :rtype: ``dict``
        """
        return await self._request(
            "post",
            f"{API_BASE}/devices/{device_id}/sov/Open",
        )

    async def close_valve(self, device_id: str) -> None:
        """Close a device shutoff valve.

        :param device_id: Unique identifier for the device
        :type device_id: ``str``
        :rtype: ``dict``
        """
        return await self._request(
            "post",
            f"{API_BASE}/devices/{device_id}/sov/Close",
        )
