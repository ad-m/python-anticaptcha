import base64

class NoCaptchaTaskProxylessTask(object):
    type = "NoCaptchaTaskProxyless"
    websiteURL = None
    websiteKey = None
    websiteSToken = None

    def __init__(self, website_url, website_key, website_s_token=None):
        self.websiteURL = website_url
        self.websiteKey = website_key
        self.websiteSToken = website_s_token

    def serialize(self):
        result = {'type': self.type,
                  'websiteURL': self.websiteURL,
                  'websiteKey': self.websiteKey,
                  'websiteSToken': self.websiteSToken or []}
        return result


class NoCaptchaTask(NoCaptchaTaskProxylessTask):
    type = "NoCaptchaTask"
    proxyType = None
    proxyAddress = None
    proxyPort = None
    proxyLogin = None
    proxyPassword = None
    userAgent = None
    cookies = None

    def __init__(self, website_url, website_key, proxy_type, proxy_address, proxy_port, user_agent,
                 proxy_login=None, proxy_password=None, cookies=None):
        super(NoCaptchaTask, self).__init__(website_url, website_key)
        self.proxyType = proxy_type
        self.proxyAddress = proxy_address
        self.proxyPort = proxy_port
        self.proxyLogin = proxy_login
        self.proxyPassword = proxy_password
        self.userAgent = user_agent
        self.cookies = cookies

    def serialize(self):
        result = super(NoCaptchaTask, self).serialize()
        result.update({'proxyType': self.proxyType,
                       'proxyAddress': self.proxyAddress,
                       'proxyPort': self.proxyPort,
                       'proxyLogin': self.proxyLogin,
                       'proxyPassword': self.proxyPassword,
                       'userAgent': self.userAgent,
                       'cookies': self.cookies})
        return result


class ImageToTextTask(object):
    type = "ImageToTextTask"
    fp = None
    phrase = None
    case = None
    numeric = None
    math = None
    minLength = None
    maxLength = None

    def __init__(self, fp, phrase=None, case=None, numeric=None, math=None, min_length=None, max_length=None):
        self.fp = fp
        self.phrase = phrase
        self.case = case
        self.numeric = numeric
        self.math = math
        self.minLength = min_length
        self.maxLength = max_length

    def serialize(self):
        return {'type': self.type,
                'body': base64.b64encode(self.fp.read()).decode('utf-8'),
                'phrase': self.phrase,
                'case': self.case,
                'numeric': self.numeric,
                'math': self.math,
                'minLength': self.minLength,
                'maxLength': self.maxLength}
