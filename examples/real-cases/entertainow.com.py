# Date of last verification: July 1, 2019
from os import environ
import re
import time
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from six.moves.urllib_parse import parse_qs
from six.moves.urllib_parse import urlparse

api_key = environ['KEY']
invisible_captcha = False
url = 'https://adserver.entertainow.com/zmgzpn.html?s=enc&rid=-502853179$154368999$vpj2QVo1SbPSpZhcqLWcKA&hsh=a705c915efcf57321a9c584ec750b03b7cf4a07a822497de6f52dddd4d1f4545&uid=58368914&sn=32768&returnUrl=https%3A%2F%2Fpf.entertainow.com%2Ff%2Fp%2Fenter%3Fplid%3D5b20522f7591fdc1418b4568%24154368956%24jPJ*pdhbyWqYdXEjWpMD.w%26euid%3D5d16abe7d50308a73e35ca76%24154368956%24oytInltQjMOz36lDm6Tt5A%26rock%3D%257B%2522fid%2522%253A%2522561544a67591fda2598b4567%2522%252C%2522puid%2522%253A%252258368914%2522%257D%26paper%3Dpq4pNV2wBaQ6jy6jsg29qWKIWEM2lgnVzrnOftOWOtWLfKu1CTN7vMxoYDsQRVETJg0UuF38SfDsIw2z8klV951ItmelQ_dXvPhNXQ5wPJkcHsRtSfXpeVzghsV3q6vjhnHVJDRu6CHuLhcGm95QPrn9VV88dpdhWDZUbUCxS7gmDAKzvc-9jeTNT4pyUd-cZRcA3Fw--6u68SRB5MdJLrhnHa8A7i_Hraya4skuUvYVw_lmT6G_MFpqCh5H-a63hxna8PotM5E%26hasRedesign%3D0%26urrMet%3Dnull%26sig%3D4026719678a6045a7f2e054c2bd1f7ee%26encl%3D370900474%26trkid%3D1108961&iasHash=OPDBQgYbFckkA3it6WJ/iQ==&forensiqHash=572919d4acd58ea12e0124b4ba4c5327&encl=370900474&plid=5b20522f7591fdc1418b4568&fid=561544a67591fda2598b4567'
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
    iframe_url = driver.find_element_by_xpath("//iframe[starts-with(@src, 'https://www.google.com/recaptcha/')]").get_attribute('src')
    site_key = parse_qs(urlparse(iframe_url).query)['k'][0]
    print("Found site-key", site_key)
    print("Send challenge")
    current_frame_url = driver.execute_script('return document.location.href')
    token = get_token(current_frame_url, site_key, False)
    callback_function = re.search('(CAPTCHA_IMMEDIATE.+?),', driver.page_source).group(1)
    driver.execute_script(
        "document.getElementById('g-recaptcha-response').innerHTML='{}';".format(token)
    )
    driver.execute_script("{}()".format(callback_function))
    time.sleep(5)
    return driver.page_source


if __name__ == '__main__':
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    options = Options()
    assert 'Close Window' in process(Firefox(firefox_options=options))
