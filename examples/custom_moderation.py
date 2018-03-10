from __future__ import unicode_literals
from os import environ

import time
from python_anticaptcha.base import SLEEP_EVERY_CHECK_FINISHED
from python_anticaptcha import AnticaptchaClient
from python_anticaptcha.fields import Radio
from python_anticaptcha.tasks import CustomCaptchaTask

api_key = environ['KEY']

"""
Note:
If you all of the content will be porn/violence, then we'd better make another task type with age filter for workers.
If it is like 1% or less, then no worries, send as CustomCaptchaTask
Reference: Ticket #16426 of Anti-captcha.com
"""


CHOICES_CONTENT = [('P', 'Porn / Nudity'),
                   ('V', 'Violence'),
                   ('O', 'Other')]
URLS = ["https://s.jawne.info.pl/captcha-nude",
        "https://s.jawne.info.pl/captcha-violence",
        "https://s.jawne.info.pl/captcha-mona-lisa"]

RESULTS = ['P',
           'V',
           'O']

form = {'content': Radio(label="Content classification", labelHint="What is visible in the picture?",
                         choices=CHOICES_CONTENT)}


def build_jobs(urls):
    client = AnticaptchaClient(api_key)
    tasks = [CustomCaptchaTask(imageUrl=url, assignment="Content moderation", form=form)
             for url in urls]
    return [client.createTask(task)
            for task in tasks]


def process_bulk(urls):
    jobs = build_jobs(urls)
    [job.join() for job in jobs]
    return [job.get_answers()['content'] for job in jobs]


def process_bulk_iter(urls):
    jobs = list(enumerate(build_jobs(urls)))
    done = []
    while len(jobs) != len(done):
        time.sleep(SLEEP_EVERY_CHECK_FINISHED)

        for i, job in jobs:
            if job in done:
                continue

            if job.check_is_ready():
                yield urls[i], job.get_answers()['content']
                done.append(job)


if __name__ == '__main__':
    result_map = dict(zip(URLS, RESULTS))
    for url, result in process_bulk_iter(URLS):
        print("{} -> {} (expected: {})".format(url, result, result_map[url]))
    print("Finished!")
