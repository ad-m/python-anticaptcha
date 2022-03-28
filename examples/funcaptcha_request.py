from six.moves.urllib import parse
import requests
from os import environ
import re

from python_anticaptcha import AnticaptchaClient, FunCaptchaTask

api_key = environ["KEY"]
site_key_pattern = 'public_key: "(.+?)",'
site_key_pattern = 'public_key: "(.+?)",'
surl_pattern = 'surl: "(.+?)",'
url = "https://client-demo.arkoselabs.com/solo-animals"
client = AnticaptchaClient(api_key)
session = requests.Session()

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
)
session.headers = {"User-Agent": UA}
proxy_url = environ["PROXY_URL"]


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
    proxy = parse_url(proxy_url)
    site_key = re.search(site_key_pattern, form_html).group(1)
    print("Determined site-key:", site_key)
    surl = re.search(surl_pattern, form_html).group(1)
    print("Determined surl:", surl)
    task = FunCaptchaTask(surl, site_key, user_agent=UA, **proxy)
    job = client.createTask(task)
    job.join(maximum_time=10**4)
    return job.get_token_response()


def form_submit(token):
    return requests.post(
        url="{}/verify".format(url),
        data={"name": "xx", "fc-token": token},
        proxies={
            "http": proxy_url,
            "https": proxy_url,
        },
    ).text


def process():
    html = get_form_html()
    token = get_token(html)
    print("Received token:", token)
    return form_submit(token)


if __name__ == "__main__":
    print("Solved!" in process())
