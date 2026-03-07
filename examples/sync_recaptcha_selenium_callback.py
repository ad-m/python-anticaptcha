import re
import time
import os
from os import environ
import gzip

from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ["KEY"]
site_key_pattern = "'sitekey': '(.+?)'"
url = "http://hcaptcha.jawne.info.pl/recaptcha.php"
EXPECTED_RESULT = '"success": true,'
client = AnticaptchaClient(api_key)

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "callback_sniffer.js"), "rb") as fp:
    wrapper_code = fp.read()


def get_token(url, site_key):
    task = NoCaptchaTaskProxylessTask(website_url=url, website_key=site_key)
    job = client.createTask(task)
    job.join(maximum_time=60 * 15)
    return job.get_solution_response()


def process(driver):
    driver.get(url)
    site_key = get_sitekey(driver)
    print("Found site-key", site_key)
    token = get_token(url, site_key)
    print("Found token", token)
    form_submit(driver, token)
    return driver.page_source


def form_submit(driver, token):
    driver.execute_script(
        "document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token)
    )
    driver.execute_script("grecaptcha.recaptchaCallback[0]('{}')".format(token))
    time.sleep(1)


def get_sitekey(driver):
    return re.search(site_key_pattern, driver.page_source).group(1)


if __name__ == "__main__":
    from seleniumwire import webdriver  # Import from seleniumwire

    def custom(req, req_body, res, res_body):
        if not req.path or not "recaptcha" in req.path:
            return
        if not res.headers.get("Content-Type", None) == "text/javascript":
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
