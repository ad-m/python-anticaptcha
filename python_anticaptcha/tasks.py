import base64


class BaseTask:
    type = None

    def serialize(self, **result):
        result["type"] = self.type
        return result


class UserAgentMixin(BaseTask):
    def __init__(self, *args, **kwargs):
        self.userAgent = kwargs.pop("user_agent")
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["userAgent"] = self.userAgent
        return data


class CookieMixin(BaseTask):
    def __init__(self, *args, **kwargs):
        self.cookies = kwargs.pop("cookies", "")
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        if self.cookies:
            data["cookies"] = self.cookies
        return data


class ProxyMixin(BaseTask):
    def __init__(self, *args, **kwargs):
        self.proxyType = kwargs.pop("proxy_type")
        self.proxyAddress = kwargs.pop("proxy_address")
        self.proxyPort = kwargs.pop("proxy_port")
        self.proxyLogin = kwargs.pop("proxy_login")
        self.proxyPassword = kwargs.pop("proxy_password")
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["proxyType"] = self.proxyType
        data["proxyAddress"] = self.proxyAddress
        data["proxyPort"] = self.proxyPort
        if self.proxyLogin:
            data["proxyLogin"] = self.proxyLogin
            data["proxyPassword"] = self.proxyPassword
        return data


class NoCaptchaTaskProxylessTask(BaseTask):
    type = "NoCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    websiteSToken = None
    recaptchaDataSValue = None

    def __init__(
        self,
        website_url,
        website_key,
        website_s_token=None,
        is_invisible=None,
        recaptcha_data_s_value=None,
        *args,
        **kwargs
    ):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.websiteSToken = website_s_token
        self.recaptchaDataSValue = recaptcha_data_s_value
        self.isInvisible = is_invisible
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
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
    type = "RecaptchaV2TaskProxyless"


class NoCaptchaTask(
    ProxyMixin, UserAgentMixin, CookieMixin, NoCaptchaTaskProxylessTask
):
    type = "NoCaptchaTask"


class RecaptchaV2Task(NoCaptchaTask):
    type = "RecaptchaV2Task"


class FunCaptchaProxylessTask(BaseTask):
    type = "FunCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    funcaptchaApiJSSubdomain = None
    data = None

    def __init__(
        self, website_url, website_key, subdomain=None, data=None, *args, **kwargs
    ):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.funcaptchaApiJSSubdomain = subdomain
        self.data = data
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websitePublicKey"] = self.websiteKey
        if self.funcaptchaApiJSSubdomain:
            data["funcaptchaApiJSSubdomain"] = self.funcaptchaApiJSSubdomain
        if self.data:
            data["data"] = self.data
        return data


class FunCaptchaTask(ProxyMixin, UserAgentMixin, CookieMixin, FunCaptchaProxylessTask):
    type = "FunCaptchaTask"


class ImageToTextTask(BaseTask):
    type = "ImageToTextTask"
    fp = None
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
        fp,
        phrase=None,
        case=None,
        numeric=None,
        math=None,
        min_length=None,
        max_length=None,
        comment=None,
        website_url=None,
        *args,
        **kwargs
    ):
        self.fp = fp
        self.phrase = phrase
        self.case = case
        self.numeric = numeric
        self.math = math
        self.minLength = min_length
        self.maxLength = max_length
        self.comment = comment
        self.websiteUrl = website_url
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["body"] = base64.b64encode(self.fp.read()).decode("utf-8")
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
    type = "RecaptchaV3TaskProxyless"
    websiteURL = None
    websiteKey = None
    minScore = None
    pageAction = None
    isEnterprise = False

    def __init__(
        self, website_url, website_key, min_score, page_action, is_enterprise=False, *args, **kwargs
    ):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.minScore = min_score
        self.pageAction = page_action
        self.isEnterprise = is_enterprise
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        data["minScore"] = self.minScore
        data["pageAction"] = self.pageAction
        data["isEnterprise"] = self.isEnterprise
        return data


class HCaptchaTaskProxyless(BaseTask):
    type = "HCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None

    def __init__(self, website_url, website_key, *args, **kwargs):
        self.websiteURL = website_url
        self.websiteKey = website_key
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        return data


class HCaptchaTask(ProxyMixin, UserAgentMixin, CookieMixin, HCaptchaTaskProxyless):
    type = "HCaptchaTask"


class RecaptchaV2EnterpriseTaskProxyless(BaseTask):
    type = "RecaptchaV2EnterpriseTaskProxyless"
    websiteURL = None
    websiteKey = None
    enterprisePayload = None
    apiDomain = None

    def __init__(self, website_url, website_key, enterprise_payload, api_domain, *args, **kwargs):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.enterprisePayload = enterprise_payload
        self.apiDomain = api_domain
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["websiteKey"] = self.websiteKey
        if self.enterprisePayload:
            data["enterprisePayload"] = self.enterprisePayload
        if self.apiDomain:
            data["apiDomain"] = self.apiDomain
        return data


class RecaptchaV2EnterpriseTask(
    ProxyMixin, UserAgentMixin, CookieMixin, RecaptchaV2EnterpriseTaskProxyless
):
    type = "RecaptchaV2EnterpriseTask"


class GeeTestTaskProxyless(BaseTask):
    type = "GeeTestTaskProxyless"
    websiteURL = None
    gt = None
    challenge = None
    geetestApiServerSubdomain = None
    geetestGetLib = None

    def __init__(
        self, website_url, gt, challenge, subdomain=None, lib=None, *args, **kwargs
    ):
        self.websiteURL = website_url
        self.gt = gt
        self.challenge = challenge
        self.geetestApiServerSubdomain = subdomain
        self.geetestGetLib = lib
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
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
    pass


class AntiGateTaskProxyless(BaseTask):
    type = "AntiGateTask"
    websiteURL = None
    templateName = None
    variables = None

    def __init__(self, website_url, template_name, variables, *args, **kwargs):
        self.websiteURL = website_url
        self.templateName = template_name
        self.variables = variables
        super().__init__(*args, **kwargs)

    def serialize(self, **result):
        data = super().serialize(**result)
        data["websiteURL"] = self.websiteURL
        data["templateName"] = self.templateName
        data["variables"] = self.variables
        return data


class AntiGateTask(ProxyMixin, AntiGateTaskProxyless):
    pass
