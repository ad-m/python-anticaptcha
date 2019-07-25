import requests
from os import environ

from python_anticaptcha import AnticaptchaClient, ImageToTextTask

api_key = environ['KEY']

URL = 'https://raw.githubusercontent.com/ad-m/python-anticaptcha/master/examples/captcha_ms.jpeg'
EXPECTED_RESULT = '56nn2'


def process(url):
    session = requests.Session()
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(session.get(url, stream=True).raw)
    job = client.createTask(task)
    job.join()
    return job.get_captcha_text()


if __name__ == '__main__':
    print("URL: " + URL)
    print("Result: " + str(process(URL)))
    print("Expected: " + str(EXPECTED_RESULT))
