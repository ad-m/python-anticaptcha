import re
from os import environ

import requests

from python_anticaptcha import AnticaptchaClient, Proxy, TurnstileTask

api_key = environ["KEY"]
proxy_url = environ["PROXY_URL"]  # eg. socks5://user:password@123.123.123.123:8888
site_key_pattern = r'data-sitekey="(.+?)"'
url = "https://example.com"  # replace with target URL
client = AnticaptchaClient(api_key)
session = requests.Session()

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
)


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    site_key = re.search(site_key_pattern, form_html).group(1)
    proxy = Proxy.parse_url(proxy_url)
    task = TurnstileTask(
        website_url=url,
        website_key=site_key,
        user_agent=UA,
        **proxy.to_kwargs(),
    )
    job = client.create_task(task)
    job.join()
    return job.get_token_response()


def form_submit(token):
    return requests.post(url, data={"cf-turnstile-response": token}).text


def process():
    html = get_form_html()
    token = get_token(html)
    return form_submit(token)


if __name__ == "__main__":
    print(process())
