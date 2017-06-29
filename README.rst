python-anticaptcha
==================

Client library for solve captchas with Anticaptcha.com support.

Getting Started
---------------

Install as standard for Python packages using:

``pip install python-annticaptcha``

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

Example snippet for text captcha:

.. code:: python

    from python_anticaptcha import AnticaptchaClient, ImageToTextTask

    api_key = '174faff8fbc769e94a5862391ecfd010'
    captcha_fp = open('examples/captcha_ms.jpeg')
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