import os
from contextlib import contextmanager
from unittest import TestCase, skipIf

import pytest
from retry import retry


def missing_key(*args, **kwargs):
    return skipIf(
        "KEY" not in os.environ,
        "Missing KEY environment variable. Unable to connect Anti-captcha.com",
    )(*args, **kwargs)


def missing_proxy(*args, **kwargs):
    return skipIf("PROXY_URL" not in os.environ, "Missing PROXY_URL environment variable")(*args, **kwargs)


@pytest.mark.e2e
@missing_key
class AntiGateTestCase(TestCase):
    @retry(tries=3)
    def test_process_antigate(self):
        from examples import sync_antigate as antigate

        solution = antigate.process()
        for key in ["url", "domain", "localStorage", "cookies", "fingerprint"]:
            self.assertIn(key, solution)


@pytest.mark.e2e
@missing_key
@missing_proxy
class FuncaptchaTestCase(TestCase):
    # CI Proxy is unstable.
    # Occasionally fails, so I repeat my attempt to have others selected.
    @retry(tries=3)
    def test_funcaptcha(self):
        from examples import sync_funcaptcha_request as funcaptcha_request

        self.assertIn("Solved!", funcaptcha_request.process())


@pytest.mark.e2e
@missing_key
class RecaptchaRequestTestCase(TestCase):
    # Anticaptcha responds is not fully reliable.
    @retry(tries=6)
    def test_process(self):
        from examples import sync_recaptcha_request as recaptcha_request

        self.assertIn(recaptcha_request.EXPECTED_RESULT, recaptcha_request.process())


@pytest.mark.e2e
@missing_key
@skipIf(True, "Anti-captcha unable to provide required score, but we tests via proxy")
class RecaptchaV3ProxylessTestCase(TestCase):
    # Anticaptcha responds is not fully reliable.
    @retry(tries=3)
    def test_process(self):
        from examples import sync_recaptcha3_request as recaptcha3_request

        self.assertTrue(recaptcha3_request.process()["success"])


@contextmanager
def open_driver(*args, **kwargs):
    from selenium.webdriver import Chrome

    driver = Chrome(*args, **kwargs)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.mark.e2e
@missing_key
class RecaptchaSeleniumtTestCase(TestCase):
    # Anticaptcha responds is not fully reliable.
    @retry(tries=6)
    def test_process(self):
        from selenium.webdriver.chrome.options import Options

        from examples import sync_recaptcha_selenium as recaptcha_selenium

        options = Options()
        options.headless = True
        options.add_experimental_option("prefs", {"intl.accept_languages": "en_US"})

        with open_driver(
            options=options,
        ) as driver:
            self.assertIn(recaptcha_selenium.EXPECTED_RESULT, recaptcha_selenium.process(driver))


@pytest.mark.e2e
@missing_key
class TextTestCase(TestCase):
    def test_process(self):
        from examples import sync_text as text

        self.assertEqual(text.process(text.IMAGE).lower(), text.EXPECTED_RESULT.lower())


@pytest.mark.e2e
@missing_key
@skipIf(True, "We testing via proxy for performance reason.")
class HCaptchaTaskProxylessTestCase(TestCase):
    @retry(tries=3)
    def test_process(self):
        from examples import sync_hcaptcha_request as hcaptcha_request

        self.assertIn(hcaptcha_request.EXPECTED_RESULT, hcaptcha_request.process())


@pytest.mark.e2e
@missing_key
@missing_proxy
class HCaptchaTaskTestCase(TestCase):
    @retry(tries=3)
    def test_process(self):
        from examples import sync_hcaptcha_request_proxy as hcaptcha_request_proxy

        self.assertIn(
            "Your request have submitted successfully.",
            hcaptcha_request_proxy.process(),
        )
