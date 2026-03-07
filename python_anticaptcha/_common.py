from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

from .exceptions import AnticaptchaException
from .tasks import BaseTask

SOFT_ID = 847
SLEEP_EVERY_CHECK_FINISHED = 3
MAXIMUM_JOIN_TIME = 60 * 5


class _BaseClientMixin:
    CREATE_TASK_URL = "/createTask"
    TASK_RESULT_URL = "/getTaskResult"
    BALANCE_URL = "/getBalance"
    REPORT_IMAGE_URL = "/reportIncorrectImageCaptcha"
    REPORT_RECAPTCHA_URL = "/reportIncorrectRecaptcha"
    APP_STAT_URL = "/getAppStats"
    SOFT_ID = SOFT_ID
    language_pool = "en"
    response_timeout = 5

    def _init_client(
        self, client_key: str | None, language_pool: str, host: str, use_ssl: bool,
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

    def _build_create_task_request(self, task: BaseTask) -> dict[str, Any]:
        return {
            "clientKey": self.client_key,
            "task": task.serialize(),
            "softId": self.SOFT_ID,
            "languagePool": self.language_pool,
        }

    def _build_key_request(self, **extra: Any) -> dict[str, Any]:
        return {"clientKey": self.client_key, **extra}

    def _process_check_response(
        self, response: dict[str, Any], client_ip: str | None = None,
    ) -> None:
        if response.get("errorId", False) == 11 and client_ip:
            response[
                "errorDescription"
            ] = "{} Your missing IP address is probably {}.".format(
                response["errorDescription"], client_ip
            )
        if response.get("errorId", False):
            raise AnticaptchaException(
                response["errorId"], response["errorCode"], response["errorDescription"]
            )

    def _repr_client(self, class_name: str) -> str:
        host = urlparse(self.base_url).hostname or self.base_url
        return f"<{class_name} host={host!r}>"


class _BaseJobMixin:
    client = None
    task_id = None
    _last_result = None

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

    def _repr_job(self, class_name: str) -> str:
        status = self._last_result.get("status") if self._last_result else None
        if status:
            return f"<{class_name} task_id={self.task_id} status={status!r}>"
        return f"<{class_name} task_id={self.task_id}>"
