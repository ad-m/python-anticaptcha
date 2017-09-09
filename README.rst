python-anticaptcha
==================

.. image:: https://www.quantifiedcode.com/api/v1/project/7cd53291667641eeb92063ad3f61f40e/badge.svg
  :target: https://www.quantifiedcode.com/app/project/7cd53291667641eeb92063ad3f61f40e
  :alt: Code issues
  
.. image:: https://img.shields.io/pypi/v/python-anticaptcha.svg
  :target: https://pypi.org/project/python-anticaptcha/
  :alt: Python package
 
Client library for solve captchas with Anticaptcha.com support. The library supports both Python 2.7 and Python 3.

Getting Started
---------------

Install as standard for Python packages using::

    pip install python-anticaptcha

Usage
-----

Do use this library do you need `Anticaptcha.com`_ API key.

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

.. _Anticaptcha.com: http://getcaptchasolution.com/ewfhjk64ll
.. _SemVer: http://semver.org/
.. _tags on this repository: https://github.com/ad-m/python-anticaptcha/tags
.. _ad-m: https://github.com/ad-m
.. _contributors: https://github.com/ad-m/python-anticaptcha/contributors
.. _LICENSE.md: LICENSE.md
