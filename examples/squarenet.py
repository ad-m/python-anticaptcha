import os
import re
import requests
from os import environ
from six.moves.urllib_parse import urljoin
from python_anticaptcha import AnticaptchaClient, SquareNetTask

api_key = environ["KEY"]
client = AnticaptchaClient(api_key)
session = requests.Session()
DIR = os.path.dirname(os.path.abspath(__file__))
filename = "{}/square.png".format(DIR)
objectName = "cat"
size = [3, 3]
EXPECTED_RESULT = [0, 4, 5, 8]


def get_image(filename):
    return open(filename, "rb")


def get_solution(fp, objectName, size):
    task = SquareNetTask(
        fp=fp, objectName=objectName, rowsCount=size[0], columnsCount=size[1],
    )
    job = client.createTask(task)
    job.join(maximum_time=9 * 60)
    return job.get_cells_numbers()


def process():
    fp = get_image(filename)
    solution = get_solution(fp, objectName, size)
    return solution


if __name__ == "__main__":
    result = process()
    print("Result: " + str(result))
    print("Expected: " + str(EXPECTED_RESULT))
    assert len(result) == len(EXPECTED_RESULT)
    for x in range(len(EXPECTED_RESULT)):
        assert result[x] is EXPECTED_RESULT[x]
    print("Processed successfully")
