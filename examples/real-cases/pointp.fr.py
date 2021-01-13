# Date of last verification: June 28, 2019
from os import environ
import time
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ['KEY']
invisible_captcha = True
site_key_pattern = 'data-sitekey="(.+?)"'
url = 'https://www.pointp.fr/)'
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
    driver.switch_to.frame(0)
    site_key = driver.find_element_by_class_name('g-recaptcha').get_attribute('data-sitekey')
    print("Found site-key", site_key)
    print("Send challenge")
    current_frame_url = driver.execute_script('return document.location.href')
    token = get_token(current_frame_url, site_key, False)
    print("Form submitted")
    driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token))
    driver.execute_script("captchaCallback()")
    time.sleep(10)
    return driver.title


if __name__ == '__main__':
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    options = Options()
    driver = Firefox(firefox_options=options)
    assert 'Error 404 | Point.P' in process(driver)
