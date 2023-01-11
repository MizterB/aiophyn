"""Define /home endpoints."""
from typing import Awaitable, Callable

from .const import API_BASE


class Home:
    """Define an object to handle the endpoints."""

    def __init__(self, request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._request: Callable[..., Awaitable] = request

    async def get_homes(
        self,
        user_id: str,
    ) -> dict:
        """Return info for all homes.

        :param user_id: Phyn username (email)
        :type user_id: ``str``
        :rtype: ``list``
        """
        params = {"user_id": user_id}

        return await self._request("get", f"{API_BASE}/homes", params=params)
