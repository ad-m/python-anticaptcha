import asyncio
import re
from os import environ

import httpx

from python_anticaptcha import AsyncAnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ["KEY"]
site_key_pattern = 'data-sitekey="(.+?)"'
url = "https://www.google.com/recaptcha/api2/demo?invisible=false"
EXPECTED_RESULT = "Verification Success... Hooray!"


async def get_form_html(session: httpx.AsyncClient) -> str:
    return (await session.get(url)).text


async def get_token(client: AsyncAnticaptchaClient, form_html: str) -> str:
    site_key = re.search(site_key_pattern, form_html).group(1)
    task = NoCaptchaTaskProxylessTask(website_url=url, website_key=site_key)
    job = await client.create_task(task)
    await job.join()
    return job.get_solution_response()


async def form_submit(session: httpx.AsyncClient, token: str) -> str:
    return (await session.post(url, data={"g-recaptcha-response": token})).text


async def process():
    async with AsyncAnticaptchaClient(api_key) as client, httpx.AsyncClient() as session:
        html = await get_form_html(session)
        token = await get_token(client, html)
        return await form_submit(session, token)


if __name__ == "__main__":
    result = asyncio.run(process())
    assert "Verification Success... Hooray!" in result
