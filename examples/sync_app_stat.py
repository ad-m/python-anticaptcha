from os import environ
from pprint import pprint
from sys import argv

from python_anticaptcha import AnticaptchaClient

api_key = environ["ANTICAPTCHA_API_KEY"]

soft_id = argv[1]
mode = argv[2]


def process(soft_id, mode):
    client = AnticaptchaClient(api_key)
    pprint(client.getAppStats(soft_id, mode))


if __name__ == "__main__":
    pprint(process(soft_id, mode))
