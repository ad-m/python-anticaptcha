from urllib.parse import urlparse

import requests
from os import environ
import re
from random import choice

from python_anticaptcha import AnticaptchaClient, FunCaptchaTask

api_key = environ['KEY']
site_key_pattern = 'data-pkey="(.+?)"'
url = 'https://www.funcaptcha.com/demo/'
client = AnticaptchaClient(api_key)
session = requests.Session()

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
session.headers = {'User-Agent': UA}
proxy_urls = environ['PROXY_URL'].split(',')


def parse_url(url):
    parsed = urlparse(url)
    return dict(
        proxy_type=parsed.scheme,
        proxy_address=parsed.hostname,
        proxy_port=parsed.port,
        proxy_login=parsed.username,
        proxy_password=parsed.password
    )


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    proxy_url = choice(proxy_urls)
    proxy = parse_url(proxy_url)

    site_key = re.search(site_key_pattern, form_html).group(1)
    task = FunCaptchaTask(url, site_key, proxy=proxy, user_agent=UA)
    job = client.createTask(task)
    job.join(maximum_time=10**4)
    return job.get_token_response()


def process():
    html = get_form_html()
    return get_token(html)


if __name__ == '__main__':
    print(process())
