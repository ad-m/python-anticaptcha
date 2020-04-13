import os
import re
import requests
from os import environ
from six.moves.urllib_parse import urljoin
from python_anticaptcha import AnticaptchaClient, SquareNetTask
from concurrent.futures import ThreadPoolExecutor


api_key = environ["KEY"]
client = AnticaptchaClient(api_key)
session = requests.Session()
DIR = os.path.dirname(os.path.abspath(__file__))
filename = "{}/square.png".format(DIR)
objectName = "cat"
size = [3, 3]
EXPECTED_RESULT = [0, 4, 5, 8]

submitted_task = 100


def compare(a, b):
    return len(a) == len(b) and all(a[x] == b[x] for x in range(len(a)))


def create_task():
    fp = open(filename, "rb")
    task = SquareNetTask(
        fp=fp, objectName=objectName, rowsCount=size[0], columnsCount=size[1],
    )
    return client.createTask(task)


def validate_solution(job):
    job.join()
    solution = job.get_cells_numbers()
    return compare(solution, EXPECTED_RESULT)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=10) as e:
        # create captcha task request
        job_futures = [e.submit(create_task) for x in range(submitted_task)]
        # fetch result for each captcha task request
        result_futures = [e.submit(validate_solution, f.result()) for f in job_futures]
        result = [f.result() for f in result_futures]

        ratio = sum(1 for x in result if x) / submitted_task
        # ratio achieved is around 0.75
        print("Success ratio: ", (ratio))
