from __future__ import annotations

import requests
import time
import json
import warnings
from typing import Any

from urllib.parse import urljoin
from .exceptions import AnticaptchaException

SLEEP_EVERY_CHECK_FINISHED = 3
MAXIMUM_JOIN_TIME = 60 * 5


class Job:
    client = None
    task_id = None
    _last_result = None

    def __init__(self, client: AnticaptchaClient, task_id: int) -> None:
        self.client = client
        self.task_id = task_id

    def _update(self) -> None:
        self._last_result = self.client.getTaskResult(self.task_id)

    def check_is_ready(self) -> bool:
        self._update()
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

    def join(self, maximum_time: int | None = None) -> None:
        elapsed_time = 0
        maximum_time = maximum_time or MAXIMUM_JOIN_TIME
        while not self.check_is_ready():
            time.sleep(SLEEP_EVERY_CHECK_FINISHED)
            elapsed_time += SLEEP_EVERY_CHECK_FINISHED
            if elapsed_time > maximum_time:
                raise AnticaptchaException(
                    None,
                    250,
                    "The execution time exceeded a maximum time of {} seconds. It takes {} seconds.".format(
                        maximum_time, elapsed_time
                    ),
                )


class AnticaptchaClient:
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
        self, client_key: str, language_pool: str = "en", host: str = "api.anti-captcha.com", use_ssl: bool = True,
    ) -> None:
        self.client_key = client_key
        self.language_pool = language_pool
        self.base_url = "{proto}://{host}/".format(
            proto="https" if use_ssl else "http", host=host
        )
        self.session = requests.Session()

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

    def createTask(self, task: Any) -> Job:
        request = {
            "clientKey": self.client_key,
            "task": task.serialize(),
            "softId": self.SOFT_ID,
            "languagePool": self.language_pool,
        }
        response = self.session.post(
            urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        ).json()
        self._check_response(response)
        return Job(self, response["taskId"])

    def createTaskSmee(self, task: Any, timeout: int = MAXIMUM_JOIN_TIME) -> Job:
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
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = self.session.post(
            urljoin(self.base_url, self.TASK_RESULT_URL), json=request
        ).json()
        self._check_response(response)
        return response

    def getBalance(self) -> float:
        request = {
            "clientKey": self.client_key,
            "softId": self.SOFT_ID,
        }
        response = self.session.post(
            urljoin(self.base_url, self.BALANCE_URL), json=request
        ).json()
        self._check_response(response)
        return response["balance"]

    def getAppStats(self, soft_id: int, mode: str) -> dict[str, Any]:
        request = {"clientKey": self.client_key, "softId": soft_id, "mode": mode}
        response = self.session.post(
            urljoin(self.base_url, self.APP_STAT_URL), json=request
        ).json()
        self._check_response(response)
        return response

    def reportIncorrectImage(self, task_id: int) -> bool:
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = self.session.post(
            urljoin(self.base_url, self.REPORT_IMAGE_URL), json=request
        ).json()
        self._check_response(response)
        return response.get("status", False) != False

    def reportIncorrectRecaptcha(self, task_id: int) -> bool:
        request = {"clientKey": self.client_key, "taskId": task_id}
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
