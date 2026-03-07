from __future__ import annotations

import json
import os
import time
import warnings
from types import TracebackType
from typing import Any, Callable, Literal
from urllib.parse import urljoin

import requests

from .exceptions import AnticaptchaException
from .tasks import BaseTask

SLEEP_EVERY_CHECK_FINISHED = 3
MAXIMUM_JOIN_TIME = 60 * 5


class Job:
    """A handle to a submitted captcha-solving task.

    Returned by :meth:`AnticaptchaClient.create_task`. Use :meth:`join` to
    wait for completion, then call one of the ``get_*`` methods to retrieve
    the solution.

    Example::

        job = client.create_task(task)
        job.join()
        print(job.get_solution_response())  # for ReCAPTCHA / hCaptcha
    """

    client: AnticaptchaClient
    task_id: int
    _last_result: dict[str, Any] | None = None

    def __init__(self, client: AnticaptchaClient, task_id: int) -> None:
        self.client = client
        self.task_id = task_id

    def _update(self) -> None:
        self._last_result = self.client.getTaskResult(self.task_id)

    def check_is_ready(self) -> bool:
        """Poll the API once and return whether the task is complete.

        :returns: ``True`` if the solution is ready, ``False`` otherwise.
        """
        self._update()
        assert self._last_result is not None
        return self._last_result["status"] == "ready"

    def get_solution_response(self) -> str:
        """Return the ``gRecaptchaResponse`` token.

        Use after solving ReCAPTCHA v2, ReCAPTCHA v3, or hCaptcha tasks.
        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]["gRecaptchaResponse"]

    def get_solution(self) -> dict[str, Any]:
        """Return the full solution dictionary from the API response.

        Useful for task types where the solution has multiple fields
        (e.g. GeeTest returns ``challenge``, ``validate``, ``seccode``).
        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]

    def get_token_response(self) -> str:
        """Return the ``token`` string from the solution.

        Use after solving FunCaptcha tasks.
        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]["token"]

    def get_answers(self) -> dict[str, str]:
        """Return the ``answers`` dictionary from the solution.

        Use after solving AntiGate tasks.
        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]["answers"]

    def get_captcha_text(self) -> str:
        """Return the recognized text from an image captcha.

        Use after solving :class:`ImageToTextTask` tasks.
        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]["text"]

    def get_cells_numbers(self) -> list[int]:
        """Return the list of selected cell numbers from a grid captcha.

        Call this only after :meth:`join` has returned.
        """
        assert self._last_result is not None
        return self._last_result["solution"]["cellNumbers"]

    def report_incorrect(self) -> bool:
        warnings.warn(
            "report_incorrect is deprecated, use report_incorrect_image instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.client.reportIncorrectImage(self.task_id)

    def report_incorrect_image(self) -> bool:
        """Report that an image captcha was solved incorrectly.

        :returns: ``True`` if the report was accepted.
        """
        return self.client.reportIncorrectImage(self.task_id)

    def report_incorrect_recaptcha(self) -> bool:
        """Report that a ReCAPTCHA was solved incorrectly.

        :returns: ``True`` if the report was accepted.
        """
        return self.client.reportIncorrectRecaptcha(self.task_id)

    def __repr__(self) -> str:
        status = self._last_result.get("status") if self._last_result else None
        if status:
            return f"<Job task_id={self.task_id} status={status!r}>"
        return f"<Job task_id={self.task_id}>"

    def join(
        self,
        maximum_time: int | None = None,
        on_check: Callable[[int, str | None], None] | None = None,
        backoff: bool = False,
    ) -> None:
        """Poll for task completion, blocking until ready or timeout.

        :param maximum_time: Maximum seconds to wait (default: ``MAXIMUM_JOIN_TIME``).
        :param on_check: Optional callback invoked after each poll with
            ``(elapsed_time, status)`` where *elapsed_time* is the total seconds
            waited so far and *status* is the last task status string
            (e.g. ``"processing"``).
        :param backoff: When ``True``, use exponential backoff for polling
            intervals starting at 1 second and doubling up to a 10-second cap.
            Default ``False`` preserves the fixed 3-second interval.
        :raises AnticaptchaException: If *maximum_time* is exceeded.
        """
        elapsed_time = 0
        maximum_time = maximum_time or MAXIMUM_JOIN_TIME
        sleep_time = 1 if backoff else SLEEP_EVERY_CHECK_FINISHED
        while not self.check_is_ready():
            time.sleep(sleep_time)
            elapsed_time += sleep_time
            if backoff:
                sleep_time = min(sleep_time * 2, 10)
            if on_check is not None and self._last_result is not None:
                on_check(elapsed_time, self._last_result.get("status"))
            if elapsed_time > maximum_time:
                raise AnticaptchaException(
                    None,
                    250,
                    f"The execution time exceeded a maximum time of {maximum_time} seconds."
                    f" It takes {elapsed_time} seconds.",
                )


class AnticaptchaClient:
    """Synchronous client for the Anticaptcha.com API.

    Create tasks, poll for results, check your balance, and report
    incorrect solutions. Can be used as a context manager to ensure the
    underlying HTTP session is closed::

        with AnticaptchaClient("my-api-key") as client:
            job = client.create_task(task)
            job.join()

    :param client_key: Your Anticaptcha API key. If omitted, the
        ``ANTICAPTCHA_API_KEY`` environment variable is used.
    :param language_pool: Language pool for workers — ``"en"`` (default)
        or ``"rn"`` (Russian).
    :param host: API hostname (default: ``"api.anti-captcha.com"``).
    :param use_ssl: Use HTTPS (default: ``True``).
    :raises AnticaptchaException: If no API key is provided.
    """

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
        self,
        client_key: str | None = None,
        language_pool: str = "en",
        host: str = "api.anti-captcha.com",
        use_ssl: bool = True,
    ) -> None:
        self.client_key = client_key or os.environ.get("ANTICAPTCHA_API_KEY")
        if not self.client_key:
            raise AnticaptchaException(
                None,
                "CONFIG_ERROR",
                "API key required. Pass client_key or set ANTICAPTCHA_API_KEY env var.",
            )
        self.language_pool = language_pool
        self.base_url = "{proto}://{host}/".format(proto="https" if use_ssl else "http", host=host)
        self.session = requests.Session()

    def __enter__(self) -> AnticaptchaClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        self.session.close()
        return False

    def close(self) -> None:
        """Close the underlying HTTP session.

        Called automatically when using the client as a context manager.
        """
        self.session.close()

    def __repr__(self) -> str:
        from urllib.parse import urlparse

        host = urlparse(self.base_url).hostname or self.base_url
        return f"<AnticaptchaClient host={host!r}>"

    @property
    def client_ip(self) -> str:
        if not hasattr(self, "_client_ip"):
            self._client_ip = self.session.get("https://api.myip.com", timeout=self.response_timeout).json()["ip"]
        return self._client_ip

    def _check_response(self, response: dict[str, Any]) -> None:
        if response.get("errorId", False) == 11:
            response["errorDescription"] = "{} Your missing IP address is probably {}.".format(
                response["errorDescription"], self.client_ip
            )
        if response.get("errorId", False):
            raise AnticaptchaException(response["errorId"], response["errorCode"], response["errorDescription"])

    def createTask(self, task: BaseTask) -> Job:
        """Submit a captcha task and return a :class:`Job` handle.

        :param task: A task instance (e.g. :class:`NoCaptchaTaskProxylessTask`).
        :returns: A :class:`Job` that can be polled with :meth:`Job.join`.
        :raises AnticaptchaException: If the API returns an error.
        """
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

    def createTaskSmee(self, task: BaseTask, timeout: int = MAXIMUM_JOIN_TIME) -> Job:
        """
        Beta method to stream response from smee.io
        """
        response = self.session.head("https://smee.io/new", timeout=self.response_timeout)
        smee_url = response.headers["Location"]
        task_data = task.serialize()
        request = {
            "clientKey": self.client_key,
            "task": task_data,
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
        create_response = self.session.post(
            url=urljoin(self.base_url, self.CREATE_TASK_URL),
            json=request,
            timeout=self.response_timeout,
        ).json()
        self._check_response(create_response)
        for line in r.iter_lines():
            content = line.decode("utf-8")
            if '"host":"smee.io"' not in content:
                continue
            payload = json.loads(content.split(":", maxsplit=1)[1].strip())
            if "taskId" not in payload["body"] or str(payload["body"]["taskId"]) != str(create_response["taskId"]):
                continue
            r.close()
            job = Job(client=self, task_id=create_response["taskId"])
            job._last_result = payload["body"]
            return job
        raise AnticaptchaException(None, 250, "No matching task response received from smee.io")

    def getTaskResult(self, task_id: int) -> dict[str, Any]:
        """Fetch the current result/status of a task.

        :param task_id: The task ID returned when the task was created.
        :returns: Raw API response dictionary with ``status`` and ``solution`` keys.
        :raises AnticaptchaException: If the API returns an error.
        """
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = self.session.post(urljoin(self.base_url, self.TASK_RESULT_URL), json=request).json()
        self._check_response(response)
        return response

    def getBalance(self) -> float:
        """Return the current account balance in USD.

        :returns: Account balance as a float (e.g. ``3.50``).
        :raises AnticaptchaException: If the API returns an error.
        """
        request = {
            "clientKey": self.client_key,
            "softId": self.SOFT_ID,
        }
        response = self.session.post(urljoin(self.base_url, self.BALANCE_URL), json=request).json()
        self._check_response(response)
        return response["balance"]

    def getAppStats(self, soft_id: int, mode: str) -> dict[str, Any]:
        """Retrieve application statistics.

        :param soft_id: Application ID.
        :param mode: Statistics mode (e.g. ``"errors"``, ``"views"``, ``"downloads"``).
        :returns: Raw API response dictionary with statistics data.
        :raises AnticaptchaException: If the API returns an error.
        """
        request = {"clientKey": self.client_key, "softId": soft_id, "mode": mode}
        response = self.session.post(urljoin(self.base_url, self.APP_STAT_URL), json=request).json()
        self._check_response(response)
        return response

    def reportIncorrectImage(self, task_id: int) -> bool:
        """Report that an image captcha was solved incorrectly.

        Use this to get a refund and improve solver accuracy.

        :param task_id: The task ID of the incorrectly solved task.
        :returns: ``True`` if the report was accepted.
        :raises AnticaptchaException: If the API returns an error.
        """
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = self.session.post(urljoin(self.base_url, self.REPORT_IMAGE_URL), json=request).json()
        self._check_response(response)
        return bool(response.get("status", False))

    def reportIncorrectRecaptcha(self, task_id: int) -> bool:
        """Report that a ReCAPTCHA was solved incorrectly.

        Use this to get a refund and improve solver accuracy.

        :param task_id: The task ID of the incorrectly solved task.
        :returns: ``True`` if the report was accepted.
        :raises AnticaptchaException: If the API returns an error.
        """
        request = {"clientKey": self.client_key, "taskId": task_id}
        response = self.session.post(urljoin(self.base_url, self.REPORT_RECAPTCHA_URL), json=request).json()
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
