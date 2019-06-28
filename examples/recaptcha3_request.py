import re
import requests
from os import environ
from six.moves.urllib_parse import urljoin
from python_anticaptcha import AnticaptchaClient, RecaptchaV3TaskProxyless

api_key = environ['KEY']
site_key_pattern = 'grecaptcha.execute\(\'(.+?)\''
action_name_pattern = '\{action: \'(.+?)\'\}'
url = 'https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php'
client = AnticaptchaClient(api_key)
session = requests.Session()


def get_form_html():
    return session.get(url).text


def get_token(form_html):
    website_key = re.search(site_key_pattern, form_html).group(1)
    page_action = re.search(action_name_pattern, form_html).group(1)
    task = RecaptchaV3TaskProxyless(
        website_url=url,
        website_key=website_key,
        page_action=page_action,
        min_score=0.7
    )
    job = client.createTask(task)
    job.join(maximum_time=9*60)
    return [page_action, job.get_solution_response()]


def form_submit(page_action, token):
    return requests.post(
        url=urljoin(url, 'recaptcha-v3-verify.php'),
        params={
            'action': page_action,
            'token': token
        }
    ).json()


def process():
    html = get_form_html()
    [page_action, token] = get_token(html)
    return form_submit(page_action, token)


if __name__ == '__main__':
    result = process()
    assert result['success'] is True
    print("Processed successfully")
