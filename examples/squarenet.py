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
    print(result)
    assert len(result) is 4
    assert result[0] is 0
    assert result[1] is 4
    assert result[2] is 5
    assert result[3] is 8
    print("Processed successfully")
