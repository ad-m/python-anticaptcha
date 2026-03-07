from six.moves.urllib import parse

import re
import requests
from os import environ

from python_anticaptcha import AnticaptchaClient, HCaptchaTask

api_key = environ["KEY"]
proxy_url = environ["PROXY_URL"]  # eg. socks5://user:password/123.123.123.123:8888/
site_key_pattern = 'data-sitekey="(.+?)"'
url = "http://hcaptcha.jawne.info.pl/"
client = AnticaptchaClient(api_key)
session = requests.Session()
EXPECTED_RESULT = "Your request have submitted successfully."

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
)


def parse_url(url):
    parsed = parse.urlparse(url)
    return dict(
        proxy_type=parsed.scheme,
        proxy_address=parsed.hostname,
        proxy_port=parsed.port,
        proxy_login=parsed.username,
        proxy_password=parsed.password,
    )


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    site_key = re.search(site_key_pattern, form_html).group(1)
    proxy = parse_url(proxy_url)
    task = HCaptchaTask(
        website_url=url,
        website_key=site_key,
        user_agent=UA,
        cookies="test=test",
        **proxy
    )
    job = client.createTask(task)
    job.join()
    return job.get_solution_response()


def form_submit(token):
    return requests.post(url, data={"g-recaptcha-response": token}).text


def process():
    html = get_form_html()
    token = get_token(html)
    return form_submit(token)


if __name__ == "__main__":
    assert EXPECTED_RESULT in process()
