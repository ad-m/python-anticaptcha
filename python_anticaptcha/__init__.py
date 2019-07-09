from .base import AnticaptchaClient
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

__version__ = '0.4.0'
