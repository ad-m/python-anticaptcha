from os import environ
from pprint import pprint
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from sys import argv

api_key = environ["KEY"]


def process():
    client = AnticaptchaClient(api_key)
    pprint(client.getBalance())


if __name__ == "__main__":
    pprint(process())
