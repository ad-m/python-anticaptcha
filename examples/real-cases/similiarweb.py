#!/usr/bin/env python
# coding: utf-8



from selenium import webdriver
from selenium.webdriver import Firefox

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
import os
import time
import re

api_key = os.environ['KEY']
# set your account / password
email = input("Enter login:")
password = input("Enter password:")

# Open web-browser
options = Options()
driver = Firefox(options=options)
driver.get('https://account.similarweb.com/login')
driver.find_element_by_css_selector('#UserName--1').send_keys(email)
driver.find_element_by_css_selector('#Password--2').send_keys(password)

# Send site-key to Anti-captcha
url = driver.current_url
site_key = re.search('"sitekey":"(.+?)"', driver.page_source).group(1)
print('Found site-key:', site_key)
client = AnticaptchaClient(api_key)
task = NoCaptchaTaskProxylessTask(url, site_key)
job = client.createTask(task)
print("Waiting to recaptcha solution")
job.join()

# Receive response
response = job.get_solution_response()
print("Received solution:", response)

# Inject response in webpage
driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
time.sleep(1) # Wait a moment to execute the script (just in case).

# Press submit button
driver.find_element_by_css_selector('#authApp > main > div > div.login__authbox > form > button').click()
