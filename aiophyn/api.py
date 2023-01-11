"""Define a base client for interacting with Phyn."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import boto3
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from pycognito.aws_srp import AWSSRP

from .const import API_BASE
from .device import Device
from .errors import RequestError
from .home import Home

_LOGGER = logging.getLogger(__name__)

DEFAULT_HEADER_CONTENT_TYPE: str = "application/json"
DEFAULT_HEADER_USER_AGENT: str = "phyn/18 CFNetwork/1331.0.7 Darwin/21.4.0"
DEFAULT_HEADER_CONNECTION: str = "keep-alive"
DEFAULT_HEADER_API_KEY: str = "E7nfOgW6VI64fYpifiZSr6Me5w1Upe155zbu4lq8"
DEFAULT_HEADER_ACCEPT: str = "application/json"
DEFAULT_HEADER_ACCEPT_ENCODING: str = "gzip, deflate, br"

COGNITO_REGION: str = "us-east-1"
COGNITO_POOL_ID: str = "us-east-1_UAv6IUsyh"
COGNITO_CLIENT_ID: str = "5q2m8ti0urmepg4lup8q0ptldq"

DEFAULT_TIMEOUT: int = 10


class API:
    """Define the API object."""

    def __init__(
        self, username: str, password: str, *, session: Optional[ClientSession] = None
    ) -> None:
        """Initialize."""
        self._username: str = username
        self._password: str = password
        self._session: ClientSession = session

        self._token: Optional[str] = None
        self._token_expiration: Optional[datetime] = None
        self._user_id: Optional[str] = None
        self._username: str = username

        self.home: Home = Home(self._request)
        self.device: Device = Device(self._request)

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        """Make a request against the API."""
        if self._token_expiration and datetime.now() >= self._token_expiration:
            _LOGGER.info("Requesting new access token to replace expired one")

            # Nullify the token so that the authentication request doesn't use it:
            self._token = None

            # Nullify the expiration so the authentication request doesn't get caught
            # here:
            self._token_expiration = None

            await self.async_authenticate()

        kwargs.setdefault("headers", {})
        kwargs["headers"].update(
            {
                "Content-Type": DEFAULT_HEADER_CONTENT_TYPE,
                "User-Agent": DEFAULT_HEADER_USER_AGENT,
                "Connection": DEFAULT_HEADER_CONNECTION,
                "x-api-key": DEFAULT_HEADER_API_KEY,
                "Accept": DEFAULT_HEADER_ACCEPT,
                "Accept-Encoding": DEFAULT_HEADER_ACCEPT_ENCODING,
            }
        )

        if self._token:
            kwargs["headers"]["Authorization"] = self._token

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(method, url, **kwargs) as resp:
                data: dict = await resp.json(content_type=None)
                resp.raise_for_status()
                return data
        except ClientError as err:
            raise RequestError(f"There was an error while requesting {url}") from err
        finally:
            if not use_running_session:
                await session.close()

    async def async_authenticate(self) -> None:
        """Authenticate the user and set the access token with its expiration."""
        client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
        aws = AWSSRP(
            username=self._username,
            password=self._password,
            pool_id=COGNITO_POOL_ID,
            client_id=COGNITO_CLIENT_ID,
            client=client,
        )
        auth_response: dict = aws.authenticate_user()

        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        expires_in = auth_response["AuthenticationResult"]["ExpiresIn"]

        self._token = access_token
        self._token_expiration = datetime.now() + timedelta(seconds=expires_in)


async def async_get_api(
    username: str, password: str, *, session: Optional[ClientSession] = None
) -> API:
    """Instantiate an authenticated API object.

    :param session: An ``aiohttp`` ``ClientSession``
    :type session: ``aiohttp.client.ClientSession``
    :param email: A Phyn email address
    :type email: ``str``
    :param password: A Phyn password
    :type password: ``str``
    :rtype: :meth:`aiophyn.api.API`
    """
    api = API(username, password, session=session)
    await api.async_authenticate()
    return api
