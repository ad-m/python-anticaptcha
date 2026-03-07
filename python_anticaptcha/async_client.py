from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any
from urllib.parse import urljoin

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for async support. "
        "Install it with: pip install python-anticaptcha[async]"
    )

from .exceptions import AnticaptchaException
from .tasks import BaseTask
from ._common import (
    _BaseClientMixin,
    _BaseJobMixin,
    SLEEP_EVERY_CHECK_FINISHED,
    MAXIMUM_JOIN_TIME,
)


class AsyncJob(_BaseJobMixin):
    def __init__(self, client: AsyncAnticaptchaClient, task_id: int) -> None:
        self.client = client
        self.task_id = task_id

    async def _update(self) -> None:
        self._last_result = await self.client.getTaskResult(self.task_id)

    async def check_is_ready(self) -> bool:
        await self._update()
        return self._last_result["status"] == "ready"

    async def report_incorrect_image(self) -> bool:
        return await self.client.reportIncorrectImage(self.task_id)

    async def report_incorrect_recaptcha(self) -> bool:
        return await self.client.reportIncorrectRecaptcha(self.task_id)

    def __repr__(self) -> str:
        return self._repr_job("AsyncJob")

    async def join(self, maximum_time: int | None = None, on_check=None) -> None:
        """Poll for task completion, sleeping asynchronously until ready or timeout.

        :param maximum_time: Maximum seconds to wait (default: ``MAXIMUM_JOIN_TIME``).
        :param on_check: Optional callback invoked after each poll with
            ``(elapsed_time, status)`` where *elapsed_time* is the total seconds
            waited so far and *status* is the last task status string
            (e.g. ``"processing"``).
        :raises AnticaptchaException: If *maximum_time* is exceeded.
        """
        elapsed_time = 0
        maximum_time = maximum_time or MAXIMUM_JOIN_TIME
        while not await self.check_is_ready():
            await asyncio.sleep(SLEEP_EVERY_CHECK_FINISHED)
            elapsed_time += SLEEP_EVERY_CHECK_FINISHED
            if on_check is not None:
                on_check(elapsed_time, self._last_result.get("status"))
            if elapsed_time > maximum_time:
                raise AnticaptchaException(
                    None,
                    250,
                    "The execution time exceeded a maximum time of {} seconds. It takes {} seconds.".format(
                        maximum_time, elapsed_time
                    ),
                )


class AsyncAnticaptchaClient(_BaseClientMixin):
    client_key = None

    def __init__(
        self, client_key: str | None = None, language_pool: str = "en", host: str = "api.anti-captcha.com", use_ssl: bool = True,
    ) -> None:
        self._init_client(client_key, language_pool, host, use_ssl)
        self.session = httpx.AsyncClient()

    async def __aenter__(self) -> AsyncAnticaptchaClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        await self.session.aclose()
        return False

    async def close(self) -> None:
        await self.session.aclose()

    def __repr__(self) -> str:
        return self._repr_client("AsyncAnticaptchaClient")

    async def _get_client_ip(self) -> str:
        if not hasattr(self, "_client_ip"):
            response = await self.session.get(
                "https://api.myip.com", timeout=self.response_timeout
            )
            self._client_ip = response.json()["ip"]
        return self._client_ip

    async def _check_response(self, response: dict[str, Any]) -> None:
        if response.get("errorId", False) == 11:
            ip = await self._get_client_ip()
            response[
                "errorDescription"
            ] = "{} Your missing IP address is probably {}.".format(
                response["errorDescription"], ip
            )
        if response.get("errorId", False):
            raise AnticaptchaException(
                response["errorId"], response["errorCode"], response["errorDescription"]
            )

    async def createTask(self, task: BaseTask) -> AsyncJob:
        request = self._build_create_task_request(task)
        response = (await self.session.post(
            urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        )).json()
        await self._check_response(response)
        return AsyncJob(self, response["taskId"])

    async def getTaskResult(self, task_id: int) -> dict[str, Any]:
        request = self._build_key_request(taskId=task_id)
        response = (await self.session.post(
            urljoin(self.base_url, self.TASK_RESULT_URL), json=request
        )).json()
        await self._check_response(response)
        return response

    async def getBalance(self) -> float:
        request = self._build_key_request(softId=self.SOFT_ID)
        response = (await self.session.post(
            urljoin(self.base_url, self.BALANCE_URL), json=request
        )).json()
        await self._check_response(response)
        return response["balance"]

    async def getAppStats(self, soft_id: int, mode: str) -> dict[str, Any]:
        request = self._build_key_request(softId=soft_id, mode=mode)
        response = (await self.session.post(
            urljoin(self.base_url, self.APP_STAT_URL), json=request
        )).json()
        await self._check_response(response)
        return response

    async def reportIncorrectImage(self, task_id: int) -> bool:
        request = self._build_key_request(taskId=task_id)
        response = (await self.session.post(
            urljoin(self.base_url, self.REPORT_IMAGE_URL), json=request
        )).json()
        await self._check_response(response)
        return response.get("status", False) != False

    async def reportIncorrectRecaptcha(self, task_id: int) -> bool:
        request = self._build_key_request(taskId=task_id)
        response = (await self.session.post(
            urljoin(self.base_url, self.REPORT_RECAPTCHA_URL), json=request
        )).json()
        await self._check_response(response)
        return response["status"] == "success"

    # Snake_case aliases
    create_task = createTask
    get_task_result = getTaskResult
    get_balance = getBalance
    get_app_stats = getAppStats
    report_incorrect_image = reportIncorrectImage
    report_incorrect_recaptcha = reportIncorrectRecaptcha
