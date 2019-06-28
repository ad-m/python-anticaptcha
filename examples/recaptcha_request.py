import re
import requests
from os import environ

from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ['KEY']
site_key_pattern = 'data-sitekey="(.+?)"'
url = 'https://www.google.com/recaptcha/api2/demo?invisible=false'
client = AnticaptchaClient(api_key)
session = requests.Session()


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    site_key = re.search(site_key_pattern, form_html).group(1)
    task = NoCaptchaTaskProxylessTask(
        website_url=url,
        website_key=site_key
    )
    job = client.createTaskSmee(task)
    return job.get_solution_response()


def form_submit(token):
    return requests.post(url, data={'g-recaptcha-response': token}).text


def process():
    html = get_form_html()
    token = get_token(html)
    return form_submit(token)


if __name__ == '__main__':
    assert 'Verification Success... Hooray!' in process()
