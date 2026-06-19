import asyncio
import re
from os import environ

import httpx

from python_anticaptcha import AsyncAnticaptchaClient, TurnstileTaskProxyless

api_key = environ["KEY"]
site_key_pattern = r'data-sitekey="(.+?)"'
url = "https://example.com"  # replace with target URL


async def get_form_html(session: httpx.AsyncClient) -> str:
    return (await session.get(url)).text


async def get_token(client: AsyncAnticaptchaClient, form_html: str) -> str:
    site_key = re.search(site_key_pattern, form_html).group(1)
    task = TurnstileTaskProxyless(website_url=url, website_key=site_key)
    job = await client.create_task(task)
    await job.join()
    return job.get_token_response()


async def form_submit(session: httpx.AsyncClient, token: str) -> str:
    return (await session.post(url, data={"cf-turnstile-response": token})).text


async def process():
    async with AsyncAnticaptchaClient(api_key) as client, httpx.AsyncClient() as session:
        html = await get_form_html(session)
        token = await get_token(client, html)
        return await form_submit(session, token)


if __name__ == "__main__":
    print(asyncio.run(process()))
