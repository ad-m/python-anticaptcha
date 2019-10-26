from .base import AnticaptchaClient
from pkg_resources import get_distribution, DistributionNotFound
from .tasks import (
    NoCaptchaTask, NoCaptchaTaskProxylessTask, ImageToTextTask,
    FunCaptchaTask, RecaptchaV3TaskProxyless
)
from .exceptions import AnticaptchaException
from .fields import (
    SimpleText, Image, WebLink, TextInput, Textarea, Checkbox, Select,
    Radio, ImageUpload
)
AnticatpchaException = AnticaptchaException

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass