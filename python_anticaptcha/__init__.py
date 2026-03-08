"""Python client library for the `Anticaptcha.com <https://anti-captcha.com>`_ API.

Solve ReCAPTCHA v2/v3, hCaptcha, FunCaptcha, GeeTest, image-to-text, and
AntiGate tasks using human workers. Supports both synchronous (``requests``)
and asynchronous (``httpx``) usage.

Quick start::

    from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

    with AnticaptchaClient("my-api-key") as client:
        task = NoCaptchaTaskProxylessTask(website_url, site_key)
        job = client.create_task(task)
        job.join()
        print(job.get_solution_response())

For async usage, install with ``pip install python-anticaptcha[async]`` and use
:class:`AsyncAnticaptchaClient`.
"""

import contextlib
from importlib.metadata import PackageNotFoundError, version

from .exceptions import AnticaptchaException
from .proxy import Proxy
from .sync_client import AnticaptchaClient, Job
from .tasks import (
    AntiGateTask,
    AntiGateTaskProxyless,
    FunCaptchaProxylessTask,
    FunCaptchaTask,
    GeeTestTask,
    GeeTestTaskProxyless,
    HCaptchaTask,
    HCaptchaTaskProxyless,
    ImageToTextTask,
    NoCaptchaTask,
    NoCaptchaTaskProxylessTask,
    RecaptchaV2EnterpriseTask,
    RecaptchaV2EnterpriseTaskProxyless,
    RecaptchaV2Task,
    RecaptchaV2TaskProxyless,
    RecaptchaV3TaskProxyless,
    TurnstileTask,
    TurnstileTaskProxyless,
)

AnticatpchaException = AnticaptchaException

with contextlib.suppress(PackageNotFoundError):
    __version__ = version(__name__)


def __getattr__(name: str) -> type:
    if name in ("AsyncAnticaptchaClient", "AsyncJob"):
        from .async_client import AsyncAnticaptchaClient, AsyncJob

        globals()["AsyncAnticaptchaClient"] = AsyncAnticaptchaClient
        globals()["AsyncJob"] = AsyncJob
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AnticaptchaClient",
    "Job",
    "Proxy",
    "NoCaptchaTaskProxylessTask",
    "RecaptchaV2TaskProxyless",
    "NoCaptchaTask",
    "RecaptchaV2Task",
    "FunCaptchaProxylessTask",
    "FunCaptchaTask",
    "ImageToTextTask",
    "RecaptchaV3TaskProxyless",
    "HCaptchaTaskProxyless",
    "HCaptchaTask",
    "RecaptchaV2EnterpriseTaskProxyless",
    "RecaptchaV2EnterpriseTask",
    "GeeTestTaskProxyless",
    "GeeTestTask",
    "AntiGateTaskProxyless",
    "AntiGateTask",
    "TurnstileTaskProxyless",
    "TurnstileTask",
    "AnticaptchaException",
    "AnticatpchaException",
    "AsyncAnticaptchaClient",
    "AsyncJob",
]
