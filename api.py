from __future__ import annotations

import logging

import requests
from requests.auth import HTTPDigestAuth

from .const import (
    API_DEVICE_STATUS,
    API_LOGIN,
    API_POWER_LIMITS,
    API_POWERUNIT,
)

_LOGGER = logging.getLogger(__name__)


class FroniusApi:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: int = 15,
    ):

        self._host = host
        self._username = username
        self._password = password
        self._timeout = timeout

        self._base = f"http://{host}"

        self._session = requests.Session()

        self._session.auth = HTTPDigestAuth(
            username,
            password,
        )

        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "HA-Fronius-EMS/0.1",
            }
        )

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    def login(self):

        url = self._url(API_LOGIN)

        _LOGGER.debug("Login %s", url)

        response = self._session.get(
            url,
            params={
                "user": self._username,
            },
            timeout=self._timeout,
        )

        _LOGGER.debug("Login status %s", response.status_code)

        response.raise_for_status()

        data = response.json()

        if not data.get("success", False):
            raise Exception("Login failed")

        _LOGGER.debug(
            "Logged in. Roles=%s",
            data["resultData"]["roles"],
        )

        return data

    def _get(self, api: str):

        response = self._session.get(
            self._url(api),
            timeout=self._timeout,
        )

        response.raise_for_status()

        return response.json()

    def _post(
        self,
        api: str,
        payload: dict,
    ):

        response = self._session.post(
            self._url(api),
            json=payload,
            timeout=self._timeout,
        )

        response.raise_for_status()

        return response.json()

    def get_power_limits(self):

        self.login()

        return self._get(API_POWER_LIMITS)

    def get_soft_limit(self):

        data = self.get_power_limits()

        return (
            data["exportLimits"]
            ["activePower"]
            ["softLimit"]
            ["powerLimit"]
        )

    def set_soft_limit(
        self,
        watts: int,
        controlled_devices: dict,
    ):

        self.login()

        payload = {
            "exportLimits": {
                "activePower": {
                    "hardLimit": {
                        "powerLimit": 0,
                    },
                    "softLimit": {
                        "powerLimit": watts,
                    },
                    "networkMode": "limitNetwork",
                },
                "autodetectedControlledDevices": controlled_devices,
                "staticControlledDevices": {},
            },
            "visualization": {
                "exportLimits": {
                    "activePower": {}
                }
            },
        }

        result = self._post(
            API_POWER_LIMITS,
            payload,
        )

        _LOGGER.debug(
            "PowerLimits response %s",
            result,
        )

        if result.get("writeFailure"):
            raise Exception(result["writeFailure"])

        if result.get("permissionFailure"):
            raise Exception(result["permissionFailure"])

        powerunit_payload = {
            "system": {
                "ACBRIDGE_MODE_POWER_OUTPUT_U16": 0
            }
        }

        result = self._post(
            API_POWERUNIT,
            powerunit_payload,
        )

        _LOGGER.debug(
            "PowerUnit response %s",
            result,
        )

        if result.get("writeFailure"):
            raise Exception(result["writeFailure"])

        if result.get("permissionFailure"):
            raise Exception(result["permissionFailure"])

        return True

    def get_device_status(
        self,
        scan: bool = False,
    ):

        self.login()

        return self._session.get(
            self._url(API_DEVICE_STATUS),
            params={
                "doScan": str(scan).lower(),
            },
            timeout=self._timeout,
        ).json()
