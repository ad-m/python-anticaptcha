import requests
from os import environ
import re
from python_anticaptcha import AnticaptchaClient, FunCaptchaTask, Proxy

api_key = environ['KEY']
site_key_pattern = 'data-pkey="(.+?)"'
url = 'https://www.funcaptcha.com/demo/'
client = AnticaptchaClient(api_key)
session = requests.Session()

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
session.headers = {'User-Agent': UA}
proxy = Proxy.parse_url("socks5://user:password@123.123.123.123:1234/")


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    site_key = re.search(site_key_pattern, form_html).group(1)
    task = FunCaptchaTask(url, site_key, proxy=proxy, user_agent=UA)
    job = client.createTask(task)
    job.join()
    return job.get_solution_response()


if __name__ == '__main__':
    html = get_form_html()
    token = get_token(html)
    print(token)
