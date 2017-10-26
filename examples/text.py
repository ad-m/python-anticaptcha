from os import environ
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

api_key = environ['KEY']


def process(path):
    captcha_fp = open(path, 'rb')
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task)
    job.join()
    return job.get_captcha_text()


if __name__ == '__main__':
    assert process('examples/captcha_ms.jpeg') == '56nn2'
