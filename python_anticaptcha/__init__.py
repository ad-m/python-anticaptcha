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
    "AnticaptchaException",
    "AnticatpchaException",
    "AsyncAnticaptchaClient",
    "AsyncJob",
]
