python-anticaptcha
==================

.. image:: https://travis-ci.org/ad-m/python-anticaptcha.svg?branch=master
  :target: https://travis-ci.org/ad-m/python-anticaptcha

.. image:: https://img.shields.io/pypi/v/python-anticaptcha.svg
  :target: https://pypi.org/project/python-anticaptcha/
  :alt: Python package

.. image:: https://badges.gitter.im/bcb/jsonrpcserver.svg
   :target: https://gitter.im/python-anticaptcha/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link
   :alt: Join the chat at https://gitter.im/python-anticaptcha/Lobby

.. image:: https://img.shields.io/pypi/pyversions/python-anticaptcha.svg
  :alt: Python compatibility
 
Client library for solve captchas with `Anticaptcha.com`_ support. The library supports both Python 2.7 and Python 3.

The library is cyclically and automatically tested for proper operation. We are constantly making the best efforts for its effective operation.

In case of any problems with integration - `create an issue`_ or contact privately.

Getting Started
---------------

Install as standard Python package using::

    pip install python-anticaptcha

Usage
-----

To use this library do you need `Anticaptcha.com`_ API key.

Recaptcha
#########

Example snippet for Recaptcha:

.. code:: python

    from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

    api_key = '174faff8fbc769e94a5862391ecfd010'
    site_key = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'  # grab from site
    url = 'https://www.google.com/recaptcha/api2/demo'

    client = AnticaptchaClient(api_key)
    task = NoCaptchaTaskProxylessTask(url, site_key)
    job = client.createTask(task)
    job.join()
    print job.get_solution_response()

The full integration example is available in file ``examples/recaptcha.py``.

Text captcha
############

Example snippet for text captcha:

.. code:: python

    from python_anticaptcha import AnticaptchaClient, ImageToTextTask

    api_key = '174faff8fbc769e94a5862391ecfd010'
    captcha_fp = open('examples/captcha_ms.jpeg', 'rb')
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task)
    job.join()
    print job.get_captcha_text()

Funcaptcha
##########

Example snippet for funcaptcha:

.. code:: python

    from python_anticaptcha import AnticaptchaClient, FunCaptchaTask, Proxy
    UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 ' \
         '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

    api_key = '174faff8fbc769e94a5862391ecfd010'
    site_key = 'DE0B0BB7-1EE4-4D70-1853-31B835D4506B'  # grab from site
    url = 'https://www.google.com/recaptcha/api2/demo'
    proxy = Proxy.parse_url("socks5://login:password@123.123.123.123")

    client = AnticaptchaClient(api_key)
    task = FunCaptchaTask(url, site_key, proxy=proxy, user_agent=user_agent)
    job = client.createTask(task)
    job.join()
    print job.get_token_response()

Report Incorrect Image
############

Example snippet for reporting an incorrect image task:

.. code:: python

    from python_anticaptcha import AnticaptchaClient, ImageToTextTask

    api_key = '174faff8fbc769e94a5862391ecfd010'
    captcha_fp = open('examples/captcha_ms.jpeg', 'rb')
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task)
    job.join()
    print job.get_captcha_text()
    job.report_incorrect()

Setup proxy
###########

The library is not responsible for managing the proxy server. However, we point to
the possibility of simply launching such a server by:

.. code::

    pip install mitmproxy
    mitmweb -p 9190 -b 0.0.0.0 --ignore '.' --socks

Next to in your application use something like:

.. code:: python

    proxy = Proxy.parse_url("socks5://123.123.123.123:9190")

We recommend entering IP-based access control for incoming addresses to proxy. IP address required by `Anticaptcha.com`_ is:

.. code::

    69.65.41.21
    209.212.146.168

Versioning
----------

We use `SemVer`_ for versioning. For the versions available, see the
`tags on this repository`_.

Authors
-------

-  **Adam Dobrawy** - *Initial work* - `ad-m`_

See also the list of `contributors`_ who participated in this project.

License
-------

This project is licensed under the MIT License - see the `LICENSE.md`_
file for details

.. _Anticaptcha.com: http://getcaptchasolution.com/i1hvnzdymd
.. _create an issue: https://github.com/ad-m/python-anticaptcha/issues/new
.. _SemVer: http://semver.org/
.. _tags on this repository: https://github.com/ad-m/python-anticaptcha/tags
.. _ad-m: https://github.com/ad-m
.. _contributors: https://github.com/ad-m/python-anticaptcha/contributors
.. _LICENSE.md: LICENSE.md
