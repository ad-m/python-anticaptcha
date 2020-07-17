from six.moves.urllib.parse import quote
from six.moves.urllib import parse

import requests
from os import environ
import re
from random import choice
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from python_anticaptcha import AnticaptchaClient, FunCaptchaTask

api_key = environ["KEY"]
site_key_pattern = 'public_key: "(.+?)",'
url = "https://client-demo.arkoselabs.com/solo-animals"
client = AnticaptchaClient(api_key)

proxy_urls = environ["PROXY_URL"].split(",")


def parse_url(url):
    parsed = parse.urlparse(url)
    return dict(
        proxy_type=parsed.scheme,
        proxy_address=parsed.hostname,
        proxy_port=parsed.port,
        proxy_login=parsed.username,
        proxy_password=parsed.password,
    )


def get_token(public_key, user_agent):
    proxy_url = choice(proxy_urls)
    proxy = parse_url(proxy_url)
    task = FunCaptchaTask(url, public_key, user_agent=user_agent, **proxy)
    job = client.createTask(task)
    job.join(maximum_time=10 ** 4)
    return job.get_token_response()


def process(driver):
    driver.get(url)
    public_key = re.search(site_key_pattern, driver.page_source).group(1)
    print("Found public-key", public_key)
    user_agent = driver.execute_script("return navigator.userAgent;")
    token = get_token(public_key, user_agent)
    print("Received token", token)
    script = """
    document.getElementById('FunCaptcha-Token').value = decodeURIComponent('{0}');
    document.getElementById('verification-token').value = decodeURIComponent('{0}');
    document.getElementById('submit-btn').disabled = false;
    """.format(
        quote(token)
    )
    driver.execute_script(script)
    driver.find_element(By.ID, "submit-btn").click()
    return driver.page_source


if __name__ == "__main__":
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    options = Options()
    # options.add_argument('-headless')
    driver = Firefox(firefox_options=options)
    assert "Solved!" in process(driver)
