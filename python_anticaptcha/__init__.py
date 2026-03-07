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
]
