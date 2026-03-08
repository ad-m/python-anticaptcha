from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, BinaryIO


class BaseTask:
    """Base class for all Anticaptcha task types.

    Each subclass represents a specific captcha type (ReCAPTCHA, hCaptcha, etc.)
    and serializes its parameters into the format expected by the Anticaptcha API.

    You do not use this class directly — instead, instantiate one of the concrete
    task classes and pass it to :meth:`AnticaptchaClient.create_task`.
    """

    type: str | None = None

    def serialize(self, **result: Any) -> dict[str, Any]:
        """Serialize the task into a dictionary for the Anticaptcha API request.

        :returns: Dictionary with task parameters including the ``type`` field.
        """
        result["type"] = self.type
        return result

    def __repr__(self) -> str:
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith("_") and v is not None}
        fields = " ".join(f"{k}={v!r}" for k, v in attrs.items())
        return f"<{self.__class__.__name__} {fields}>"


class UserAgentMixin(BaseTask):
    """Mixin that adds a ``user_agent`` parameter to a task.

    Required by proxy-enabled task variants so the captcha solver can
    emulate the same browser.

    :param user_agent: Browser User-Agent string to use when solving.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.userAgent: str = kwargs.pop("user_agent")
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["userAgent"] = self.userAgent
        return data


class CookieMixin(BaseTask):
    """Mixin that adds an optional ``cookies`` parameter to a task.

    Pass cookies when the target page requires them for the captcha to render
    correctly.

    :param cookies: Cookie string to include with the request (optional).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.cookies: str = kwargs.pop("cookies", "")
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        if self.cookies:
            data["cookies"] = self.cookies
        return data


class ProxyMixin(BaseTask):
    """Mixin that adds proxy parameters to a task.

    Use this (via proxy-enabled task variants like :class:`NoCaptchaTask`) when
    the captcha must be solved through a specific proxy. You can build the
    keyword arguments conveniently with :meth:`Proxy.to_kwargs`.

    :param proxy_type: Proxy protocol — ``"http"``, ``"socks4"``, or ``"socks5"``.
    :param proxy_address: Proxy server hostname or IP address.
    :param proxy_port: Proxy server port.
    :param proxy_login: Username for proxy authentication (empty string if none).
    :param proxy_password: Password for proxy authentication (empty string if none).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.proxyType: str = kwargs.pop("proxy_type")
        self.proxyAddress: str = kwargs.pop("proxy_address")
        self.proxyPort: int = kwargs.pop("proxy_port")
        self.proxyLogin: str = kwargs.pop("proxy_login")
        self.proxyPassword: str = kwargs.pop("proxy_password")
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["proxyType"] = self.proxyType
        data["proxyAddress"] = self.proxyAddress
        data["proxyPort"] = self.proxyPort
        if self.proxyLogin:
            data["proxyLogin"] = self.proxyLogin
            data["proxyPassword"] = self.proxyPassword
        return data


class NoCaptchaTaskProxylessTask(BaseTask):
    """Solve a Google ReCAPTCHA v2 challenge without a proxy.

    This is the most common task type. The solver will access the target page
    directly from Anticaptcha's servers.

    After the job completes, retrieve the token with
    :meth:`Job.get_solution_response`.

    :param website_url: Full URL of the page where the captcha appears.
    :param website_key: The ``data-sitekey`` value from the ReCAPTCHA element.
    :param website_s_token: Optional ``data-s`` token for Google Search captchas.
    :param is_invisible: Set to ``True`` for invisible ReCAPTCHA. The system
        auto-detects this, so the parameter is optional.
    :param recaptcha_data_s_value: Value of the ``data-s`` parameter if present.

    Example::

        task = NoCaptchaTaskProxylessTask(
            website_url="https://example.com",
            website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        )
    """

    type = "NoCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    websiteSToken = None
    recaptchaDataSValue = None

    def __init__(
        self,
        website_url: str,
        website_key: str,
        website_s_token: str | None = None,
        is_invisible: bool | None = None,
        recaptcha_data_s_value: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.websiteSToken = website_s_token
        self.recaptchaDataSValue = recaptcha_data_s_value
        self.isInvisible = is_invisible
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        if self.websiteSToken is not None:
            data["websiteSToken"] = self.websiteSToken
        if self.isInvisible is not None:
            data["isInvisible"] = self.isInvisible
        if self.recaptchaDataSValue is not None:
            data["recaptchaDataSValue"] = self.recaptchaDataSValue
        return data


class RecaptchaV2TaskProxyless(NoCaptchaTaskProxylessTask):
    """Solve a Google ReCAPTCHA v2 challenge without a proxy (newer API type name).

    Identical to :class:`NoCaptchaTaskProxylessTask` but uses the updated
    ``RecaptchaV2TaskProxyless`` type identifier.
    """

    type = "RecaptchaV2TaskProxyless"


class NoCaptchaTask(ProxyMixin, UserAgentMixin, CookieMixin, NoCaptchaTaskProxylessTask):
    """Solve a Google ReCAPTCHA v2 challenge through a proxy.

    Same as :class:`NoCaptchaTaskProxylessTask` but additionally requires
    proxy and user-agent parameters. Use :class:`Proxy` to build the proxy
    keyword arguments conveniently::

        proxy = Proxy.parse_url("socks5://user:pass@host:port")
        task = NoCaptchaTask(url, site_key, user_agent=UA, **proxy.to_kwargs())

    :param user_agent: Browser User-Agent string.
    :param cookies: Optional cookie string (default: ``""``).
    :param proxy_type: Proxy protocol (``"http"``, ``"socks4"``, ``"socks5"``).
    :param proxy_address: Proxy server hostname or IP.
    :param proxy_port: Proxy server port.
    :param proxy_login: Proxy username (empty string if none).
    :param proxy_password: Proxy password (empty string if none).
    """

    type = "NoCaptchaTask"


class RecaptchaV2Task(NoCaptchaTask):
    """Solve a Google ReCAPTCHA v2 challenge through a proxy (newer API type name).

    Identical to :class:`NoCaptchaTask` but uses the updated
    ``RecaptchaV2Task`` type identifier.
    """

    type = "RecaptchaV2Task"


class FunCaptchaProxylessTask(BaseTask):
    """Solve an Arkose Labs FunCaptcha challenge without a proxy.

    After the job completes, retrieve the token with
    :meth:`Job.get_token_response`.

    :param website_url: Full URL of the page where the captcha appears.
    :param website_key: The FunCaptcha public key (e.g.
        ``"DE0B0BB7-1EE4-4D70-1853-31B835D4506B"``).
    :param subdomain: Custom FunCaptcha API subdomain, if the site uses one
        (e.g. ``"mysite-api.arkoselabs.com"``).
    :param data: Additional data blob required by some FunCaptcha implementations.
    """

    type = "FunCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    funcaptchaApiJSSubdomain = None
    data = None

    def __init__(
        self,
        website_url: str,
        website_key: str,
        subdomain: str | None = None,
        data: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.funcaptchaApiJSSubdomain = subdomain
        self.data = data
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websitePublicKey"] = self.websiteKey
        if self.funcaptchaApiJSSubdomain:
            data["funcaptchaApiJSSubdomain"] = self.funcaptchaApiJSSubdomain
        if self.data:
            data["data"] = self.data
        return data


class FunCaptchaTask(ProxyMixin, UserAgentMixin, CookieMixin, FunCaptchaProxylessTask):
    """Solve an Arkose Labs FunCaptcha challenge through a proxy.

    Same as :class:`FunCaptchaProxylessTask` but additionally requires
    proxy, user-agent, and optional cookie parameters.
    """

    type = "FunCaptchaTask"


class ImageToTextTask(BaseTask):
    """Solve a classic image-based captcha by extracting text from an image.

    The image is automatically base64-encoded. You can pass a file path,
    raw ``bytes``, or an open binary file object.

    After the job completes, retrieve the text with
    :meth:`Job.get_captcha_text`.

    :param image: Captcha image as a file path (``str`` or ``Path``), raw
        ``bytes``, or a binary file-like object.
    :param phrase: ``True`` if the answer contains multiple words.
    :param case: ``True`` if the answer is case-sensitive.
    :param numeric: ``0`` — no requirements, ``1`` — numbers only,
        ``2`` — letters only.
    :param math: ``True`` if the captcha is a math expression to solve.
    :param min_length: Minimum number of characters in the answer.
    :param max_length: Maximum number of characters in the answer.
    :param comment: Hint text shown to the worker (e.g. ``"Enter red letters"``).
    :param website_url: URL of the page where the captcha was found (optional,
        used for context).

    Example::

        task = ImageToTextTask("captcha.png")
        task = ImageToTextTask(open("captcha.png", "rb").read())
    """

    type = "ImageToTextTask"
    _body = None
    phrase = None
    case = None
    numeric = None
    math = None
    minLength = None
    maxLength = None
    comment = None
    websiteUrl = None

    def __init__(
        self,
        image: str | Path | bytes | BinaryIO,
        phrase: bool | None = None,
        case: bool | None = None,
        numeric: int | None = None,
        math: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        comment: str | None = None,
        website_url: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if isinstance(image, (str, Path)):
            with open(image, "rb") as f:
                self._body = base64.b64encode(f.read()).decode("utf-8")
        elif isinstance(image, bytes):
            self._body = base64.b64encode(image).decode("utf-8")
        else:
            self._body = base64.b64encode(image.read()).decode("utf-8")
        self.phrase = phrase
        self.case = case
        self.numeric = numeric
        self.math = math
        self.minLength = min_length
        self.maxLength = max_length
        self.comment = comment
        self.websiteUrl = website_url
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["body"] = self._body
        if self.phrase is not None:
            data["phrase"] = self.phrase
        if self.case is not None:
            data["case"] = self.case
        if self.numeric is not None:
            data["numeric"] = self.numeric
        if self.math is not None:
            data["math"] = self.math
        if self.minLength is not None:
            data["minLength"] = self.minLength
        if self.maxLength is not None:
            data["maxLength"] = self.maxLength
        if self.comment is not None:
            data["comment"] = self.comment
        if self.websiteUrl is not None:
            data["websiteUrl"] = self.websiteUrl
        return data


class RecaptchaV3TaskProxyless(BaseTask):
    """Solve a Google ReCAPTCHA v3 challenge (score-based, proxyless only).

    ReCAPTCHA v3 returns a score (0.0–1.0) rather than a visual challenge.
    You must specify the minimum acceptable score and the page action.

    After the job completes, retrieve the token with
    :meth:`Job.get_solution_response`.

    :param website_url: Full URL of the page where the captcha appears.
    :param website_key: The ``data-sitekey`` value from the ReCAPTCHA element.
    :param min_score: Minimum score threshold (e.g. ``0.3``, ``0.7``, ``0.9``).
    :param page_action: The action value from ``grecaptcha.execute(key, {action: ...})``.
    :param is_enterprise: Set to ``True`` if the site uses the Enterprise version
        of ReCAPTCHA v3.
    """

    type = "RecaptchaV3TaskProxyless"
    websiteURL = None
    websiteKey = None
    minScore = None
    pageAction = None
    isEnterprise = False

    def __init__(
        self,
        website_url: str,
        website_key: str,
        min_score: float,
        page_action: str,
        is_enterprise: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.minScore = min_score
        self.pageAction = page_action
        self.isEnterprise = is_enterprise
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        data["minScore"] = self.minScore
        data["pageAction"] = self.pageAction
        data["isEnterprise"] = self.isEnterprise
        return data


class HCaptchaTaskProxyless(BaseTask):
    """Solve an hCaptcha challenge without a proxy.

    After the job completes, retrieve the token with
    :meth:`Job.get_solution_response`.

    :param website_url: Full URL of the page where the captcha appears.
    :param website_key: The ``data-sitekey`` value from the hCaptcha element.
    """

    type = "HCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None

    def __init__(self, website_url: str, website_key: str, *args: Any, **kwargs: Any) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        return data


class HCaptchaTask(ProxyMixin, UserAgentMixin, CookieMixin, HCaptchaTaskProxyless):
    """Solve an hCaptcha challenge through a proxy.

    Same as :class:`HCaptchaTaskProxyless` but additionally requires
    proxy, user-agent, and optional cookie parameters.
    """

    type = "HCaptchaTask"


class RecaptchaV2EnterpriseTaskProxyless(BaseTask):
    """Solve a Google ReCAPTCHA v2 Enterprise challenge without a proxy.

    Use this for sites that use the Enterprise version of ReCAPTCHA v2.

    After the job completes, retrieve the token with
    :meth:`Job.get_solution_response`.

    :param website_url: Full URL of the page where the captcha appears.
    :param website_key: The ``data-sitekey`` value from the ReCAPTCHA element.
    :param enterprise_payload: Optional dictionary with Enterprise-specific
        parameters (e.g. ``{"s": "...", "action": "..."}``) or ``None``.
    :param api_domain: Custom API domain if the site uses a non-standard
        ReCAPTCHA endpoint (e.g. ``"recaptcha.net"``) or ``None``.
    """

    type = "RecaptchaV2EnterpriseTaskProxyless"
    websiteURL = None
    websiteKey = None
    enterprisePayload = None
    apiDomain = None

    def __init__(
        self,
        website_url: str,
        website_key: str,
        enterprise_payload: dict[str, Any] | None,
        api_domain: str | None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.enterprisePayload = enterprise_payload
        self.apiDomain = api_domain
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        if self.enterprisePayload:
            data["enterprisePayload"] = self.enterprisePayload
        if self.apiDomain:
            data["apiDomain"] = self.apiDomain
        return data


class RecaptchaV2EnterpriseTask(ProxyMixin, UserAgentMixin, CookieMixin, RecaptchaV2EnterpriseTaskProxyless):
    """Solve a Google ReCAPTCHA v2 Enterprise challenge through a proxy.

    Same as :class:`RecaptchaV2EnterpriseTaskProxyless` but additionally requires
    proxy, user-agent, and optional cookie parameters.
    """

    type = "RecaptchaV2EnterpriseTask"


class GeeTestTaskProxyless(BaseTask):
    """Solve a GeeTest (slide / click) captcha without a proxy.

    After the job completes, use :meth:`Job.get_solution` to get the full
    solution dictionary containing ``challenge``, ``validate``, and ``seccode``.

    :param website_url: Full URL of the page where the captcha appears.
    :param gt: The ``gt`` parameter value from the GeeTest script.
    :param challenge: The ``challenge`` token obtained from the GeeTest API.
    :param subdomain: Custom GeeTest API subdomain, if the site uses one.
    :param lib: Custom ``getLib`` parameter value, if required.
    """

    type = "GeeTestTaskProxyless"
    websiteURL = None
    gt = None
    challenge = None
    geetestApiServerSubdomain = None
    geetestGetLib = None

    def __init__(
        self,
        website_url: str,
        gt: str,
        challenge: str,
        subdomain: str | None = None,
        lib: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.gt = gt
        self.challenge = challenge
        self.geetestApiServerSubdomain = subdomain
        self.geetestGetLib = lib
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["gt"] = self.gt
        data["challenge"] = self.challenge
        if self.geetestApiServerSubdomain:
            data["geetestApiServerSubdomain"] = self.geetestApiServerSubdomain
        if self.geetestGetLib:
            data["geetestGetLib"] = self.geetestGetLib
        return data


class GeeTestTask(ProxyMixin, UserAgentMixin, GeeTestTaskProxyless):
    """Solve a GeeTest captcha through a proxy.

    Same as :class:`GeeTestTaskProxyless` but additionally requires
    proxy and user-agent parameters.
    """

    type = "GeeTestTask"


class AntiGateTaskProxyless(BaseTask):
    """Solve a custom AntiGate task using a predefined template.

    AntiGate tasks use templates to automate complex browser-based actions.
    Browse available templates at https://anti-captcha.com/antigate.

    After the job completes, use :meth:`Job.get_solution` to get the full
    solution dictionary.

    :param website_url: Full URL of the page to process.
    :param template_name: Name of the AntiGate template
        (e.g. ``"Sign up on MailChimp"``).
    :param variables: Dictionary of template variables (keys and values
        depend on the template).
    """

    type = "AntiGateTask"
    websiteURL = None
    templateName = None
    variables = None

    def __init__(
        self,
        website_url: str,
        template_name: str,
        variables: dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.templateName = template_name
        self.variables = variables
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["templateName"] = self.templateName
        data["variables"] = self.variables
        return data


class TurnstileTaskProxyless(BaseTask):
    """Solve a Cloudflare Turnstile challenge without a proxy.

    Turnstile is Cloudflare's CAPTCHA replacement used on millions of websites.
    The service automatically detects all Turnstile subtypes (manual,
    non-interactive, invisible).

    After the job completes, retrieve the token with
    :meth:`Job.get_token_response`.

    :param website_url: Full URL of the page where the Turnstile widget appears.
    :param website_key: The Turnstile ``sitekey`` from the page source.
    :param action: Optional action parameter passed to the Turnstile widget.
    :param cdata: Optional ``cData`` token for Cloudflare-protected pages.
    :param chl_page_data: Optional ``chlPageData`` token for Cloudflare pages.

    Example::

        task = TurnstileTaskProxyless(
            website_url="https://example.com",
            website_key="0x4AAAAAAABS7vwvV6VFfMcD",
        )
    """

    type = "TurnstileTaskProxyless"
    websiteURL = None
    websiteKey = None

    def __init__(
        self,
        website_url: str,
        website_key: str,
        action: str | None = None,
        cdata: str | None = None,
        chl_page_data: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.action = action
        self.cData = cdata
        self.chlPageData = chl_page_data
        super().__init__(*args, **kwargs)

    def serialize(self, **result: Any) -> dict[str, Any]:
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        if self.action is not None:
            data["action"] = self.action
        if self.cData is not None:
            data["cData"] = self.cData
        if self.chlPageData is not None:
            data["chlPageData"] = self.chlPageData
        return data


class TurnstileTask(ProxyMixin, UserAgentMixin, CookieMixin, TurnstileTaskProxyless):
    """Solve a Cloudflare Turnstile challenge through a proxy.

    Same as :class:`TurnstileTaskProxyless` but additionally requires
    proxy, user-agent, and optional cookie parameters.

    Note that the proxy-based approach is slower and requires high-quality,
    self-hosted proxies.

    :param user_agent: Browser User-Agent string.
    :param cookies: Optional cookie string (default: ``""``).
    :param proxy_type: Proxy protocol (``"http"``, ``"socks4"``, ``"socks5"``).
    :param proxy_address: Proxy server hostname or IP.
    :param proxy_port: Proxy server port.
    :param proxy_login: Proxy username (empty string if none).
    :param proxy_password: Proxy password (empty string if none).
    """

    type = "TurnstileTask"


class AntiGateTask(ProxyMixin, AntiGateTaskProxyless):
    """Solve a custom AntiGate task through a proxy.

    Same as :class:`AntiGateTaskProxyless` but additionally requires
    proxy parameters.
    """
