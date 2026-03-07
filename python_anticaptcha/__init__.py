from importlib.metadata import version, PackageNotFoundError

from .base import AnticaptchaClient, Job
from .proxy import Proxy
from .tasks import (
    NoCaptchaTaskProxylessTask,
    RecaptchaV2TaskProxyless,
    NoCaptchaTask,
    RecaptchaV2Task,
    FunCaptchaProxylessTask,
    FunCaptchaTask,
    ImageToTextTask,
    RecaptchaV3TaskProxyless,
    HCaptchaTaskProxyless,
    HCaptchaTask,
    RecaptchaV2EnterpriseTaskProxyless,
    RecaptchaV2EnterpriseTask,
    GeeTestTaskProxyless,
    GeeTestTask,
    AntiGateTaskProxyless,
    AntiGateTask,
)
from .exceptions import AnticaptchaException

AnticatpchaException = AnticaptchaException

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass


def __getattr__(name: str):
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
    "AnticaptchaException",
    "AnticatpchaException",
    "AsyncAnticaptchaClient",
    "AsyncJob",
]
