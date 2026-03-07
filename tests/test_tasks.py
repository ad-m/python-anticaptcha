import io

from python_anticaptcha.tasks import (
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

PROXY_KWARGS = dict(
    proxy_type="http",
    proxy_address="1.2.3.4",
    proxy_port=8080,
    proxy_login="user",
    proxy_password="pass",
)

USER_AGENT_KWARGS = dict(user_agent="Mozilla/5.0")


class TestNoCaptchaTaskProxylessTask:
    def test_type(self):
        task = NoCaptchaTaskProxylessTask(website_url="https://example.com", website_key="key123")
        data = task.serialize()
        assert data["type"] == "NoCaptchaTaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["websiteKey"] == "key123"

    def test_optional_fields_omitted(self):
        task = NoCaptchaTaskProxylessTask(website_url="https://example.com", website_key="key123")
        data = task.serialize()
        assert "websiteSToken" not in data
        assert "isInvisible" not in data
        assert "recaptchaDataSValue" not in data

    def test_optional_fields_included(self):
        task = NoCaptchaTaskProxylessTask(
            website_url="https://example.com",
            website_key="key123",
            website_s_token="stoken",
            is_invisible=True,
            recaptcha_data_s_value="svalue",
        )
        data = task.serialize()
        assert data["websiteSToken"] == "stoken"
        assert data["isInvisible"] is True
        assert data["recaptchaDataSValue"] == "svalue"


class TestRecaptchaV2TaskProxyless:
    def test_type(self):
        task = RecaptchaV2TaskProxyless(website_url="https://example.com", website_key="key123")
        assert task.serialize()["type"] == "RecaptchaV2TaskProxyless"


class TestNoCaptchaTask:
    def test_type_and_proxy(self):
        task = NoCaptchaTask(
            website_url="https://example.com",
            website_key="key123",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        data = task.serialize()
        assert data["type"] == "NoCaptchaTask"
        assert data["proxyType"] == "http"
        assert data["proxyAddress"] == "1.2.3.4"
        assert data["proxyPort"] == 8080
        assert data["proxyLogin"] == "user"
        assert data["proxyPassword"] == "pass"
        assert data["userAgent"] == "Mozilla/5.0"


class TestRecaptchaV2Task:
    def test_type(self):
        task = RecaptchaV2Task(
            website_url="https://example.com",
            website_key="key123",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        assert task.serialize()["type"] == "RecaptchaV2Task"


class TestFunCaptchaProxylessTask:
    def test_type_and_required_fields(self):
        task = FunCaptchaProxylessTask(website_url="https://example.com", website_key="pubkey")
        data = task.serialize()
        assert data["type"] == "FunCaptchaTaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["websitePublicKey"] == "pubkey"
        assert "funcaptchaApiJSSubdomain" not in data
        assert "data" not in data

    def test_optional_fields(self):
        task = FunCaptchaProxylessTask(
            website_url="https://example.com",
            website_key="pubkey",
            subdomain="sub.example.com",
            data="extra",
        )
        data = task.serialize()
        assert data["funcaptchaApiJSSubdomain"] == "sub.example.com"
        assert data["data"] == "extra"


class TestFunCaptchaTask:
    def test_type(self):
        task = FunCaptchaTask(
            website_url="https://example.com",
            website_key="pubkey",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        assert task.serialize()["type"] == "FunCaptchaTask"


class TestImageToTextTask:
    def test_serialize_base64(self):
        fp = io.BytesIO(b"fake image data")
        task = ImageToTextTask(fp)
        data = task.serialize()
        assert data["type"] == "ImageToTextTask"
        assert data["body"] == "ZmFrZSBpbWFnZSBkYXRh"

    def test_from_bytes(self):
        task = ImageToTextTask(b"fake image data")
        data = task.serialize()
        assert data["type"] == "ImageToTextTask"
        assert data["body"] == "ZmFrZSBpbWFnZSBkYXRh"

    def test_from_file_path(self, tmp_path):
        img = tmp_path / "captcha.jpeg"
        img.write_bytes(b"fake image data")
        task = ImageToTextTask(str(img))
        data = task.serialize()
        assert data["body"] == "ZmFrZSBpbWFnZSBkYXRh"

    def test_from_pathlib_path(self, tmp_path):
        img = tmp_path / "captcha.jpeg"
        img.write_bytes(b"fake image data")
        task = ImageToTextTask(img)
        data = task.serialize()
        assert data["body"] == "ZmFrZSBpbWFnZSBkYXRh"

    def test_optional_fields_omitted(self):
        task = ImageToTextTask(b"data")
        data = task.serialize()
        for key in ["phrase", "case", "numeric", "math", "minLength", "maxLength", "comment", "websiteUrl"]:
            assert key not in data

    def test_optional_fields_included(self):
        task = ImageToTextTask(
            b"data",
            phrase=True,
            case=True,
            numeric=1,
            math=False,
            min_length=3,
            max_length=10,
            comment="solve this",
            website_url="https://example.com",
        )
        data = task.serialize()
        assert data["phrase"] is True
        assert data["case"] is True
        assert data["numeric"] == 1
        assert data["math"] is False
        assert data["minLength"] == 3
        assert data["maxLength"] == 10
        assert data["comment"] == "solve this"
        assert data["websiteUrl"] == "https://example.com"


class TestRecaptchaV3TaskProxyless:
    def test_serialize(self):
        task = RecaptchaV3TaskProxyless(
            website_url="https://example.com",
            website_key="key123",
            min_score=0.9,
            page_action="verify",
        )
        data = task.serialize()
        assert data["type"] == "RecaptchaV3TaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["websiteKey"] == "key123"
        assert data["minScore"] == 0.9
        assert data["pageAction"] == "verify"
        assert data["isEnterprise"] is False

    def test_enterprise_flag(self):
        task = RecaptchaV3TaskProxyless(
            website_url="https://example.com",
            website_key="key123",
            min_score=0.3,
            page_action="login",
            is_enterprise=True,
        )
        assert task.serialize()["isEnterprise"] is True


class TestHCaptchaTaskProxyless:
    def test_serialize(self):
        task = HCaptchaTaskProxyless(website_url="https://example.com", website_key="hkey")
        data = task.serialize()
        assert data["type"] == "HCaptchaTaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["websiteKey"] == "hkey"


class TestHCaptchaTask:
    def test_type(self):
        task = HCaptchaTask(
            website_url="https://example.com",
            website_key="hkey",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        assert task.serialize()["type"] == "HCaptchaTask"


class TestRecaptchaV2EnterpriseTaskProxyless:
    def test_required_fields(self):
        task = RecaptchaV2EnterpriseTaskProxyless(
            website_url="https://example.com",
            website_key="ekey",
            enterprise_payload=None,
            api_domain=None,
        )
        data = task.serialize()
        assert data["type"] == "RecaptchaV2EnterpriseTaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["websiteKey"] == "ekey"
        assert "enterprisePayload" not in data
        assert "apiDomain" not in data

    def test_optional_fields(self):
        task = RecaptchaV2EnterpriseTaskProxyless(
            website_url="https://example.com",
            website_key="ekey",
            enterprise_payload={"s": "value"},
            api_domain="recaptcha.net",
        )
        data = task.serialize()
        assert data["enterprisePayload"] == {"s": "value"}
        assert data["apiDomain"] == "recaptcha.net"


class TestRecaptchaV2EnterpriseTask:
    def test_type(self):
        task = RecaptchaV2EnterpriseTask(
            website_url="https://example.com",
            website_key="ekey",
            enterprise_payload=None,
            api_domain=None,
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        assert task.serialize()["type"] == "RecaptchaV2EnterpriseTask"


class TestGeeTestTaskProxyless:
    def test_required_fields(self):
        task = GeeTestTaskProxyless(website_url="https://example.com", gt="gt123", challenge="ch456")
        data = task.serialize()
        assert data["type"] == "GeeTestTaskProxyless"
        assert data["websiteURL"] == "https://example.com"
        assert data["gt"] == "gt123"
        assert data["challenge"] == "ch456"
        assert "geetestApiServerSubdomain" not in data
        assert "geetestGetLib" not in data

    def test_optional_fields(self):
        task = GeeTestTaskProxyless(
            website_url="https://example.com",
            gt="gt123",
            challenge="ch456",
            subdomain="api.geetest.com",
            lib="getlib.js",
        )
        data = task.serialize()
        assert data["geetestApiServerSubdomain"] == "api.geetest.com"
        assert data["geetestGetLib"] == "getlib.js"


class TestGeeTestTask:
    def test_type(self):
        task = GeeTestTask(
            website_url="https://example.com",
            gt="gt123",
            challenge="ch456",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        assert task.serialize()["type"] == "GeeTestTask"


class TestAntiGateTaskProxyless:
    def test_serialize(self):
        task = AntiGateTaskProxyless(
            website_url="https://example.com",
            template_name="my_template",
            variables={"var1": "val1", "var2": "val2"},
        )
        data = task.serialize()
        assert data["type"] == "AntiGateTask"
        assert data["websiteURL"] == "https://example.com"
        assert data["templateName"] == "my_template"
        assert data["variables"] == {"var1": "val1", "var2": "val2"}


class TestAntiGateTask:
    def test_type(self):
        task = AntiGateTask(
            website_url="https://example.com",
            template_name="tmpl",
            variables={},
            **PROXY_KWARGS,
        )
        # AntiGateTask doesn't set type explicitly, inherits AntiGateTask type
        assert task.serialize()["type"] == "AntiGateTask"


class TestProxyMixin:
    def test_proxy_login_omitted_when_falsy(self):
        task = NoCaptchaTask(
            website_url="https://example.com",
            website_key="key123",
            proxy_type="http",
            proxy_address="1.2.3.4",
            proxy_port=8080,
            proxy_login="",
            proxy_password="",
            user_agent="Mozilla/5.0",
        )
        data = task.serialize()
        assert "proxyLogin" not in data
        assert "proxyPassword" not in data
        assert data["proxyType"] == "http"
        assert data["proxyAddress"] == "1.2.3.4"
        assert data["proxyPort"] == 8080


class TestCookieMixin:
    def test_cookies_omitted_when_empty(self):
        task = NoCaptchaTask(
            website_url="https://example.com",
            website_key="key123",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        data = task.serialize()
        assert "cookies" not in data

    def test_cookies_included_when_set(self):
        task = NoCaptchaTask(
            website_url="https://example.com",
            website_key="key123",
            cookies="session=abc",
            **USER_AGENT_KWARGS,
            **PROXY_KWARGS,
        )
        data = task.serialize()
        assert data["cookies"] == "session=abc"
