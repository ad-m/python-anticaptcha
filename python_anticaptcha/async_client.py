from __future__ import annotations

import asyncio
import os
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
from .base import SLEEP_EVERY_CHECK_FINISHED, MAXIMUM_JOIN_TIME


class AsyncJob:
    client = None
    task_id = None
    _last_result = None

    def __init__(self, client: AsyncAnticaptchaClient, task_id: int) -> None:
        self.client = client
        self.task_id = task_id

    async def _update(self) -> None:
        self._last_result = await self.client.getTaskResult(self.task_id)

    async def check_is_ready(self) -> bool:
        await self._update()
        return self._last_result["status"] == "ready"

    def get_solution_response(self) -> str:  # Recaptcha
        return self._last_result["solution"]["gRecaptchaResponse"]

    def get_solution(self) -> dict[str, Any]:
        return self._last_result["solution"]

    def get_token_response(self) -> str:  # Funcaptcha
        return self._last_result["solution"]["token"]

    def get_answers(self) -> dict[str, str]:
        return self._last_result["solution"]["answers"]

    def get_captcha_text(self) -> str:  # Image
        return self._last_result["solution"]["text"]

    def get_cells_numbers(self) -> list[int]:
        return self._last_result["solution"]["cellNumbers"]

    async def report_incorrect_image(self) -> bool:
        return await self.client.reportIncorrectImage(self.task_id)

    async def report_incorrect_recaptcha(self) -> bool:
        return await self.client.reportIncorrectRecaptcha(self.task_id)

    def __repr__(self) -> str:
        status = self._last_result.get("status") if self._last_result else None
        if status:
            return f"<AsyncJob task_id={self.task_id} status={status!r}>"
        return f"<AsyncJob task_id={self.task_id}>"

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


class AsyncAnticaptchaClient:
    client_key = None
    CREATE_TASK_URL = "/createTask"
    TASK_RESULT_URL = "/getTaskResult"
    BALANCE_URL = "/getBalance"
    REPORT_IMAGE_URL = "/reportIncorrectImageCaptcha"
    REPORT_RECAPTCHA_URL = "/reportIncorrectRecaptcha"
    APP_STAT_URL = "/getAppStats"
    SOFT_ID = 847
    language_pool = "en"
    response_timeout = 5

    def __init__(
        self, client_key: str | None = None, language_pool: str = "en", host: str = "api.anti-captcha.com", use_ssl: bool = True,
    ) -> None:
        self.client_key = client_key or os.environ.get("ANTICAPTCHA_API_KEY")
        if not self.client_key:
            raise AnticaptchaException(
                None,
                "CONFIG_ERROR",
                "API key required. Pass client_key or set ANTICAPTCHA_API_KEY env var.",
            )
        self.language_pool = language_pool
        self.base_url = "{proto}://{host}/".format(
            proto="https" if use_ssl else "http", host=host
        )
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
        from urllib.parse import urlparse
        host = urlparse(self.base_url).hostname or self.base_url
        return f"<AsyncAnticaptchaClient host={host!r}>"

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
        request = {
            "clientKey": self.client_key,
            "task": task.serialize(),
            "softId": self.SOFT_ID,
            "languagePool": self.language_pool,
        }
        response = (await self.session.post(
            urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        )).json()
        await self._check_response(response)
        return AsyncJob(self, response["taskId"])

    async def getTaskResult(self, task_id: int) -> dict[str, Any]:
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = (await self.session.post(
            urljoin(self.base_url, self.TASK_RESULT_URL), json=request
        )).json()
        await self._check_response(response)
        return response

    async def getBalance(self) -> float:
        request = {
            "clientKey": self.client_key,
            "softId": self.SOFT_ID,
        }
        response = (await self.session.post(
            urljoin(self.base_url, self.BALANCE_URL), json=request
        )).json()
        await self._check_response(response)
        return response["balance"]

    async def getAppStats(self, soft_id: int, mode: str) -> dict[str, Any]:
        request = {"clientKey": self.client_key, "softId": soft_id, "mode": mode}
        response = (await self.session.post(
            urljoin(self.base_url, self.APP_STAT_URL), json=request
        )).json()
        await self._check_response(response)
        return response

    async def reportIncorrectImage(self, task_id: int) -> bool:
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = (await self.session.post(
            urljoin(self.base_url, self.REPORT_IMAGE_URL), json=request
        )).json()
        await self._check_response(response)
        return response.get("status", False) != False

    async def reportIncorrectRecaptcha(self, task_id: int) -> bool:
        request = {"clientKey": self.client_key, "taskId": task_id}
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
