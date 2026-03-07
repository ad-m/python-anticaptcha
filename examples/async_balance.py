import asyncio
from os import environ
from pprint import pprint

from python_anticaptcha import AsyncAnticaptchaClient

api_key = environ["KEY"]


async def process():
    async with AsyncAnticaptchaClient(api_key) as client:
        balance = await client.get_balance()
        pprint(balance)


if __name__ == "__main__":
    asyncio.run(process())
