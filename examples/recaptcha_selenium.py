import time
from os import environ

from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = environ['KEY']
invisible_captcha = True
url = 'https://www.google.com/recaptcha/api2/demo?invisible={}'.format(str(invisible_captcha))
client = AnticaptchaClient(api_key)


def get_token(url, site_key, invisible):
    task = NoCaptchaTaskProxylessTask(
        website_url=url,
        website_key=site_key,
        is_invisible=invisible
    )
    job = client.createTask(task)
    job.join()
    return job.get_solution_response()


def process(driver):
    driver.get(url)
    site_key = get_sitekey(driver)
    print("Found site-key", site_key)
    token = get_token(url, site_key, invisible_captcha)
    print("Found token", token)
    form_submit(driver, token)
    return driver.find_element_by_class_name('recaptcha-success').text


def form_submit(driver, token):
    driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token))
    driver.execute_script("onSuccess('{}')".format(token))
    time.sleep(1)


def get_sitekey(driver):
    return driver. \
        find_element_by_class_name('g-recaptcha'). \
        get_attribute('data-sitekey')


if __name__ == '__main__':
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    options = Options()
    # options.add_argument('-headless')
    driver = Firefox(firefox_options=options)
    assert 'Verification Success... Hooray!' in process(driver)
