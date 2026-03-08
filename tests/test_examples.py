import os
from contextlib import contextmanager
from unittest import TestCase, skipIf

import pytest
from retry import retry


def missing_key(*args, **kwargs):
    return skipIf(
        "ANTICAPTCHA_API_KEY" not in os.environ,
        "Missing ANTICAPTCHA_API_KEY environment variable. Unable to connect Anti-captcha.com",
    )(*args, **kwargs)


def missing_proxy(*args, **kwargs):
    return skipIf("PROXY_URL" not in os.environ, "Missing PROXY_URL environment variable")(*args, **kwargs)


@pytest.mark.e2e
@missing_key
class AntiGateTestCase(TestCase):
    @retry(tries=3)
    def test_process_antigate(self):
        from examples import sync_antigate

        solution = sync_antigate.process()
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
        from examples import sync_funcaptcha_request

        self.assertIn("Solved!", sync_funcaptcha_request.process())


@pytest.mark.e2e
@missing_key
class RecaptchaRequestTestCase(TestCase):
    # Anticaptcha responds is not fully reliable.
    @retry(tries=6)
    def test_process(self):
        from examples import sync_recaptcha_request

        self.assertIn(sync_recaptcha_request.EXPECTED_RESULT, sync_recaptcha_request.process())


@pytest.mark.e2e
@missing_key
@skipIf(True, "Anti-captcha unable to provide required score, but we tests via proxy")
class RecaptchaV3ProxylessTestCase(TestCase):
    # Anticaptcha responds is not fully reliable.
    @retry(tries=3)
    def test_process(self):
        from examples import sync_recaptcha3_request

        self.assertTrue(sync_recaptcha3_request.process()["success"])


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

        from examples import sync_recaptcha_selenium

        options = Options()
        options.headless = True
        options.add_experimental_option("prefs", {"intl.accept_languages": "en_US"})

        with open_driver(
            options=options,
        ) as driver:
            self.assertIn(sync_recaptcha_selenium.EXPECTED_RESULT, sync_recaptcha_selenium.process(driver))


@pytest.mark.e2e
@missing_key
class TextTestCase(TestCase):
    def test_process(self):
        from examples import sync_text

        self.assertEqual(sync_text.process(sync_text.IMAGE).lower(), sync_text.EXPECTED_RESULT.lower())


@pytest.mark.e2e
@missing_key
@skipIf(True, "We testing via proxy for performance reason.")
class HCaptchaTaskProxylessTestCase(TestCase):
    @retry(tries=3)
    def test_process(self):
        from examples import sync_hcaptcha_request

        self.assertIn(sync_hcaptcha_request.EXPECTED_RESULT, sync_hcaptcha_request.process())


@pytest.mark.e2e
@missing_key
@missing_proxy
class HCaptchaTaskTestCase(TestCase):
    @retry(tries=3)
    def test_process(self):
        from examples import sync_hcaptcha_request_proxy

        self.assertIn(
            "Your request have submitted successfully.",
            sync_hcaptcha_request_proxy.process(),
        )
