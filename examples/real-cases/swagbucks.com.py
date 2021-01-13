# Date of last verification: June 28, 2019
import re
from os import environ

from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ['KEY']
invisible_captcha = True
url = 'https://www.swagbucks.com/p/login'
client = AnticaptchaClient(api_key)


def get_token(website_url, site_key, invisible):
    task = NoCaptchaTaskProxylessTask(
        website_url=website_url,
        website_key=site_key,
        is_invisible=invisible
    )
    job = client.createTask(task)
    job.join()
    return job.get_solution_response()


def process(driver):
    driver.get(url)
    site_key = re.search("captchaSitekey = '(.+?)'",driver.page_source).group(1)
    print("Found site-key", site_key)
    print("Send challenge")
    token = get_token(driver.current_url, site_key, invisible_captcha)
    print("Received challenge-response")
    driver.find_element_by_xpath('//*[@id="sbxJxRegEmail"]').send_keys('email@test.com')
    driver.find_element_by_xpath('//*[@id="sbxJxRegPswd"]').send_keys('password')
    driver.find_element_by_xpath('//*[@id="loginBtn"]').click()
    print("Form submitted")
    driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token))
    driver.execute_script("document.getElementById('loginForm').submit()")
    return driver.find_element_by_xpath('//*[@id="divErLandingPage"]').text


if __name__ == '__main__':
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    options = Options()
    # options.add_argument('-headless')
    driver = Firefox(firefox_options=options)
    assert 'Incorrect Email/Password Combination' in process(driver)
