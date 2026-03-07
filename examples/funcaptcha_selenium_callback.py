import gzip
import os
import re
import time
from os import environ

from selenium.webdriver.common.by import By
from six.moves.urllib.parse import quote

from python_anticaptcha import AnticaptchaClient, FunCaptchaProxylessTask

api_key = environ["KEY"]
site_key_pattern = 'public_key: "(.+?)",'
url = "https://client-demo.arkoselabs.com/solo-animals"
EXPECTED_RESULT = "Solved!"
client = AnticaptchaClient(api_key)

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "callback_sniffer.js"), "rb") as fp:
    wrapper_code = fp.read()


def get_token(url, site_key):
    task = FunCaptchaProxylessTask(website_url=url, website_key=site_key)
    job = client.createTask(task)
    job.join(maximum_time=60 * 15)
    return job.get_token_response()


def process(driver):
    driver.get(url)
    site_key = get_sitekey(driver)
    print("Found site-key", site_key)
    token = get_token(url, site_key)
    print("Found token", token)
    form_submit(driver, token)
    return driver.page_source


def form_submit(driver, token):
    script = """
    document.getElementById('FunCaptcha-Token').value = decodeURIComponent('{0}');
    document.getElementById('verification-token').value = decodeURIComponent('{0}');
    document.getElementById('submit-btn').disabled = false;
    """.format(
        quote(token)
    )
    time.sleep(1)
    # as example call callback - not required in that example
    driver.execute_script(f"ArkoseEnforcement.funcaptchaCallback[0]('{token}')")
    driver.find_element(By.ID, "submit-btn").click()
    time.sleep(1)


def get_sitekey(driver):
    return re.search(site_key_pattern, driver.page_source).group(1)


if __name__ == "__main__":
    from seleniumwire import webdriver  # Import from seleniumwire

    def custom(req, req_body, res, res_body):
        if not req.path:
            return
        if "arkoselabs" not in req.path:
            return
        if res.headers.get("Content-Type", None) not in [
            "text/javascript",
            "application/javascript",
        ]:
            print(
                "Skip invalid content type",
                req.path,
                res.headers.get("Content-Type", None),
            )
            return
        if res.headers["Content-Encoding"] == "gzip":
            del res.headers["Content-Encoding"]
            res_body = gzip.decompress(res_body)
        return res_body + wrapper_code

    driver = webdriver.Firefox(seleniumwire_options={"custom_response_handler": custom})

    try:
        assert EXPECTED_RESULT in process(driver)
    finally:
        driver.close()
