from __future__ import annotations

import requests
import time
import json
import warnings
from types import TracebackType
from typing import Any

from urllib.parse import urljoin
from .exceptions import AnticaptchaException
from .tasks import BaseTask
from ._common import (
    _BaseClientMixin,
    _BaseJobMixin,
    SOFT_ID,
    SLEEP_EVERY_CHECK_FINISHED,
    MAXIMUM_JOIN_TIME,
)


class Job(_BaseJobMixin):
    def __init__(self, client: AnticaptchaClient, task_id: int) -> None:
        self.client = client
        self.task_id = task_id

    def _update(self) -> None:
        self._last_result = self.client.getTaskResult(self.task_id)

    def check_is_ready(self) -> bool:
        self._update()
        return self._last_result["status"] == "ready"

    def report_incorrect(self) -> bool:
        warnings.warn(
            "report_incorrect is deprecated, use report_incorrect_image instead",
            DeprecationWarning,
        )
        return self.client.reportIncorrectImage()

    def report_incorrect_image(self) -> bool:
        return self.client.reportIncorrectImage(self.task_id)

    def report_incorrect_recaptcha(self) -> bool:
        return self.client.reportIncorrectRecaptcha(self.task_id)

    def __repr__(self) -> str:
        return self._repr_job("Job")

    def join(self, maximum_time: int | None = None, on_check=None) -> None:
        """Poll for task completion, blocking until ready or timeout.

        :param maximum_time: Maximum seconds to wait (default: ``MAXIMUM_JOIN_TIME``).
        :param on_check: Optional callback invoked after each poll with
            ``(elapsed_time, status)`` where *elapsed_time* is the total seconds
            waited so far and *status* is the last task status string
            (e.g. ``"processing"``).
        :raises AnticaptchaException: If *maximum_time* is exceeded.
        """
        elapsed_time = 0
        maximum_time = maximum_time or MAXIMUM_JOIN_TIME
        while not self.check_is_ready():
            time.sleep(SLEEP_EVERY_CHECK_FINISHED)
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


class AnticaptchaClient(_BaseClientMixin):
    client_key = None

    def __init__(
        self, client_key: str | None = None, language_pool: str = "en", host: str = "api.anti-captcha.com", use_ssl: bool = True,
    ) -> None:
        self._init_client(client_key, language_pool, host, use_ssl)
        self.session = requests.Session()

    def __enter__(self) -> AnticaptchaClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        self.session.close()
        return False

    def close(self) -> None:
        self.session.close()

    def __repr__(self) -> str:
        return self._repr_client("AnticaptchaClient")

    @property
    def client_ip(self) -> str:
        if not hasattr(self, "_client_ip"):
            self._client_ip = self.session.get(
                "https://api.myip.com", timeout=self.response_timeout
            ).json()["ip"]
        return self._client_ip

    def _check_response(self, response: dict[str, Any]) -> None:
        if response.get("errorId", False) == 11:
            response[
                "errorDescription"
            ] = "{} Your missing IP address is probably {}.".format(
                response["errorDescription"], self.client_ip
            )
        if response.get("errorId", False):
            raise AnticaptchaException(
                response["errorId"], response["errorCode"], response["errorDescription"]
            )

    def createTask(self, task: BaseTask) -> Job:
        request = self._build_create_task_request(task)
        response = self.session.post(
            urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        ).json()
        self._check_response(response)
        return Job(self, response["taskId"])

    def createTaskSmee(self, task: BaseTask, timeout: int = MAXIMUM_JOIN_TIME) -> Job:
        """
        Beta method to stream response from smee.io
        """
        response = self.session.head(
            "https://smee.io/new", timeout=self.response_timeout
        )
        smee_url = response.headers["Location"]
        task = task.serialize()
        request = {
            "clientKey": self.client_key,
            "task": task,
            "softId": self.SOFT_ID,
            "languagePool": self.language_pool,
            "callbackUrl": smee_url,
        }
        r = self.session.get(
            url=smee_url,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=(self.response_timeout, timeout),
        )
        response = self.session.post(
            url=urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        ).json()
        self._check_response(response)
        for line in r.iter_lines():
            content = line.decode("utf-8")
            if '"host":"smee.io"' not in content:
                continue
            payload = json.loads(content.split(":", maxsplit=1)[1].strip())
            if "taskId" not in payload["body"] or str(payload["body"]["taskId"]) != str(
                response["taskId"]
            ):
                continue
            r.close()
            job = Job(client=self, task_id=response["taskId"])
            job._last_result = payload["body"]
            return job

    def getTaskResult(self, task_id: int) -> dict[str, Any]:
        request = self._build_key_request(taskId=task_id)
        response = self.session.post(
            urljoin(self.base_url, self.TASK_RESULT_URL), json=request
        ).json()
        self._check_response(response)
        return response

    def getBalance(self) -> float:
        request = self._build_key_request(softId=self.SOFT_ID)
        response = self.session.post(
            urljoin(self.base_url, self.BALANCE_URL), json=request
        ).json()
        self._check_response(response)
        return response["balance"]

    def getAppStats(self, soft_id: int, mode: str) -> dict[str, Any]:
        request = self._build_key_request(softId=soft_id, mode=mode)
        response = self.session.post(
            urljoin(self.base_url, self.APP_STAT_URL), json=request
        ).json()
        self._check_response(response)
        return response

    def reportIncorrectImage(self, task_id: int) -> bool:
        request = self._build_key_request(taskId=task_id)
        response = self.session.post(
            urljoin(self.base_url, self.REPORT_IMAGE_URL), json=request
        ).json()
        self._check_response(response)
        return response.get("status", False) != False

    def reportIncorrectRecaptcha(self, task_id: int) -> bool:
        request = self._build_key_request(taskId=task_id)
        response = self.session.post(
            urljoin(self.base_url, self.REPORT_RECAPTCHA_URL), json=request
        ).json()
        self._check_response(response)
        return response["status"] == "success"

    # Snake_case aliases
    create_task = createTask
    create_task_smee = createTaskSmee
    get_task_result = getTaskResult
    get_balance = getBalance
    get_app_stats = getAppStats
    report_incorrect_image = reportIncorrectImage
    report_incorrect_recaptcha = reportIncorrectRecaptcha
