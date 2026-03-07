# python-anticaptcha

[![Build Status](https://github.com/ad-m/python-anticaptcha/workflows/Python%20package/badge.svg)](https://github.com/ad-m/python-anticaptcha/actions?workflow=Python+package)
[![PyPI](https://img.shields.io/pypi/v/python-anticaptcha.svg)](https://pypi.org/project/python-anticaptcha/)
[![Chat](https://badges.gitter.im/python-anticaptcha/Lobby.svg)](https://gitter.im/python-anticaptcha/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link)
[![Python compatibility](https://img.shields.io/pypi/pyversions/python-anticaptcha.svg)](https://github.com/ad-m/python-anticaptcha/blob/master/setup.py)

Client library for solve captchas with [Anticaptcha.com support](http://getcaptchasolution.com/i1hvnzdymd).
The library requires Python >= 3.9.

The library is cyclically and automatically tested for proper operation. We are constantly making the best efforts for its effective operation.

In case of any problems with integration - [read the documentation](http://python-anticaptcha.readthedocs.io/en/latest/), [create an issue](https://github.com/ad-m/python-anticaptcha/issues/new), use [Gitter](https://gitter.im/python-anticaptcha/Lobby) or contact privately.

## Getting Started

Install as standard Python package using:

```
pip install python-anticaptcha
```

## Usage

To use this library do you need [Anticaptcha.com](http://getcaptchasolution.com/p9bwplkicx) API key.

You can pass the key explicitly or set the `ANTICAPTCHA_API_KEY` environment variable:

```python
# Explicit key
client = AnticaptchaClient("my-api-key")

# Or set ANTICAPTCHA_API_KEY environment variable
client = AnticaptchaClient()
```

### Solve recaptcha

Example snippet for Recaptcha:

```python
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = '174faff8fbc769e94a5862391ecfd010'
site_key = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'  # grab from site
url = 'https://www.google.com/recaptcha/api2/demo'

client = AnticaptchaClient(api_key)
task = NoCaptchaTaskProxylessTask(url, site_key)
job = client.create_task(task)
job.join()
print(job.get_solution_response())
```

The full integration example is available in file `examples/recaptcha.py`.

If you only process few page many times to increase reliability, you can specify
whether the captcha is visible or not. This parameter is not required, as is the
system detects invisible sitekeys automatically, and needs several recursive
measures for automated training and analysis. For provide that pass
`is_invisible` parameter to `NoCaptchaTaskProxylessTask` or `NoCaptchaTask` eg.:

```python
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

api_key = '174faff8fbc769e94a5862391ecfd010'
site_key = '6Lc-0DYUAAAAAOPM3RGobCfKjIE5STmzvZfHbbNx'  # grab from site
url = 'https://losangeles.craigslist.org/lac/kid/d/housekeeper-sitting-pet-care/6720136191.html'

client = AnticaptchaClient(api_key)
task = NoCaptchaTaskProxylessTask(url, site_key, is_invisible=True)
job = client.create_task(task)
job.join()
print(job.get_solution_response())
```

### Solve text captcha

Example snippet for text captcha:

```python
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

api_key = '174faff8fbc769e94a5862391ecfd010'
captcha_fp = open('examples/captcha_ms.jpeg', 'rb')
client = AnticaptchaClient(api_key)
task = ImageToTextTask(captcha_fp)
job = client.create_task(task)
job.join()
print(job.get_captcha_text())
```

### Solve funcaptcha

Example snippet for funcaptcha:

```python
from python_anticaptcha import AnticaptchaClient, FunCaptchaTask, Proxy
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

api_key = '174faff8fbc769e94a5862391ecfd010'
site_key = 'DE0B0BB7-1EE4-4D70-1853-31B835D4506B'  # grab from site
url = 'https://www.google.com/recaptcha/api2/demo'
proxy = Proxy.parse_url("socks5://login:password@123.123.123.123:1080")

client = AnticaptchaClient(api_key)
task = FunCaptchaTask(url, site_key, user_agent=UA, **proxy.to_kwargs())
job = client.create_task(task)
job.join()
print(job.get_token_response())
```

### Report incorrect image

Example snippet for reporting an incorrect image task:

```python
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

api_key = '174faff8fbc769e94a5862391ecfd010'
captcha_fp = open('examples/captcha_ms.jpeg', 'rb')
client = AnticaptchaClient(api_key)
task = ImageToTextTask(captcha_fp)
job = client.create_task(task)
job.join()
print(job.get_captcha_text())
job.report_incorrect_image()
```

### Setup proxy

The library is not responsible for managing the proxy server. However, we point to
the possibility of simply launching such a server by:

```
pip install mitmproxy
mitmweb -p 9190 -b 0.0.0.0 --ignore '.' --socks
```

Next to in your application use something like:

```python
proxy = Proxy.parse_url("socks5://123.123.123.123:9190")
```

We recommend entering IP-based access control for incoming addresses to proxy. IP address required by
[Anticaptcha.com](http://getcaptchasolution.com/p9bwplkicx) is:

```
69.65.41.21
209.212.146.168
```

### Error handling

In the event of an application error, the `AnticaptchaException` exception is thrown. To handle the exception, do the following:

```python
from python_anticaptcha import AnticaptchaException, ImageToTextTask

try:
    # any actions
except AnticaptchaException as e:
    if e.error_code == 'ERROR_ZERO_BALANCE':
        notify_about_no_funds(e.error_id, e.error_code, e.error_description)
    else:
        raise
```

> **Note:** The legacy misspelled `AnticatpchaException` alias is still available for backward compatibility.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/ad-m/python-anticaptcha/tags).

## Authors

- **Adam Dobrawy** - *Initial work* - [ad-m](https://github.com/ad-m)

See also the list of [contributors](https://github.com/ad-m/python-anticaptcha/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md)
file for details
