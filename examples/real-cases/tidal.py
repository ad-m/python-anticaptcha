from urllib.parse import urlparse, quote

import requests
from os import environ
import re
from random import choice
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

API_KEY = environ['KEY']
LOGIN = input('Enter login:')
PASSWORD = input('Enter password:')

options = Options()
# options.add_argument('-headless')
driver = Firefox(firefox_options=options)

# Open Tidal login form
driver.get("https://listen.tidal.com/login")
driver.implicitly_wait(5)

# Enter email
import pdb; pdb.set_trace();
WebDriverWait(driver, 120).until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@id = 'email']")
    )
).send_keys(LOGIN)

# Extract site-key
site_key = re.search('"recaptchaKey":"(.+?)"', driver.page_source).group(1)

# Solve challenge with help of python-anticaptcha
url=driver.current_url
client = AnticaptchaClient(API_KEY)
task = NoCaptchaTaskProxylessTask(url, site_key)
job = client.createTask(task)
job.join()
response = job.get_solution_response()
print("Received solution", response)

# Inject solution
driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='{}';".format(response))

# Submit form with login and challenge
driver.find_element(By.XPATH, '//button[contains(@class,"btn-client-primary")]').click()

# Enter password
password=WebDriverWait(driver, 120).until(
    EC.presence_of_element_located(
        (By.ID, "password")
    )
).send_keys(PASSWORD)

# Submit form with password
driver.find_element(By.XPATH, '//button[contains(@class,"btn-success")]').click()

# Success! User logged in!
input('Press ENTER to continue')