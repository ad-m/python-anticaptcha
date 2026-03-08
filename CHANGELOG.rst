Changelog
=========

Unreleased
----------

Added
#####

- Add ``TurnstileTaskProxyless`` and ``TurnstileTask`` for solving Cloudflare Turnstile captchas (with optional ``action``, ``cdata``, and ``chl_page_data`` parameters)
- Add ``AsyncAnticaptchaClient`` and ``AsyncJob`` for async/await usage with ``httpx`` (``pip install python-anticaptcha[async]``)
- Rename ``base.py`` → ``sync_client.py`` for symmetry with ``async_client.py``; backward-compatible ``base.py`` shim preserved
- Rename sync example files with ``sync_`` prefix to match ``async_`` examples
- Add context manager support to ``AnticaptchaClient`` (``__enter__``, ``__exit__``, ``close``)
- Add ``ANTICAPTCHA_API_KEY`` environment variable fallback for ``AnticaptchaClient``
- Add ``Proxy`` frozen dataclass with ``parse_url()`` and ``to_kwargs()`` methods
- Add snake_case aliases: ``create_task``, ``create_task_smee``, ``get_balance``, ``get_app_stats``
- Add ``py.typed`` marker and complete type annotations (`#124 <https://github.com/ad-m/python-anticaptcha/pull/124>`_)
- Add ``__repr__`` to ``Job``, ``AnticaptchaClient``, and ``BaseTask`` (`#123 <https://github.com/ad-m/python-anticaptcha/pull/123>`_)
- Add optional ``on_check`` callback to ``Job.join()`` (`#125 <https://github.com/ad-m/python-anticaptcha/pull/125>`_)
- ``ImageToTextTask`` now accepts file paths (``str``/``Path``), raw bytes, or file-like objects

Changed
#######

- **Breaking:** Minimum Python version increased from 2.7+ to 3.9+
- Migrate from ``setup.py`` / ``setup.cfg`` to ``pyproject.toml`` (PEP 621) (`#122 <https://github.com/ad-m/python-anticaptcha/pull/122>`_)
- Switch README from RST to Markdown (`#126 <https://github.com/ad-m/python-anticaptcha/pull/126>`_)
- Switch test runner from nose2 to pytest
- Switch PyPI publishing to trusted publishing via GitHub Actions (`#114 <https://github.com/ad-m/python-anticaptcha/pull/114>`_)
- Fix ``RecaptchaV2EnterpriseTask`` missing proxyless base class inheritance
- Fix ``ImageToTextTask.serialize()`` sending ``None`` values
- Fix ``GeeTestTask`` incorrect inheritance
- Fix ``AntiGateTaskProxyless`` super() call
- Remove redundant cookies serialization in ``ProxyMixin``
- Use Python 3 ``super()`` without arguments throughout codebase

Removed
#######

- Drop Python 2.7 and Python 3.4-3.8 support
- Remove ``six`` dependency (replaced with stdlib ``urllib.parse``)
- Remove ``compat.py`` module
- Remove legacy ``setup.py`` and ``setup.cfg``

1.0.0 - 2022-03-28
------------------

Added
#####

- Add new tasks:

  - ``AntiGateTask`` and ``AntiGateTaskProxyless``
  - ``RecaptchaV2EnterpriseTask`` and ``RecaptchaV2EnterpriseTaskProxyless``
  - ``GeeTestTask`` and ``GeeTestTaskProxyless``
  - ``RecaptchaV2Task`` (alias of ``NoCaptchaTask``) and ``RecaptchaV2TaskProxyless`` (alias of ``NoCaptchaTaskProxyless``)

- Add example for ``AntiGateTaskProxyless``
- Add optional parameters ``comment``, ``websiteUrl`` to ``ImageToTextTask``
- Add optional parameter ``funcaptchaApiJSSubdomain``, ``data`` to ``FunCaptchaTask*``
- Add optional parameter ``isEnterprise`` to ``RecaptchaV3Task*``

Removed
#######

- Drop tasks unsupported upstream: ``CustomCaptchaTask``, ``SquareNetTask``

Changed
#######

- Internal refactor to extract ``UserAgentMixin``, ``CookieMixin``
- Use nose2 for tests

0.7.1 - 2020-07-17
------------------

Added
#####

- Added examples for proxy mode including `hcaptcha_request_proxy`

Changed
#######

- Fix inheritance of `FunCaptchaTask`
- Added `FunCaptchaTask` to e2e tests

0.7.0 - 2020-06-08
------------------

Added
#####

-  Added parameter `recaptchaDataSValue` in `NoCaptchaTask*`
   
   Thanks to this change added support for additional "data-s"  used by some custom
   ReCaptcha deployments, which is in fact a one-time token and must be grabbed
   every time you want to solve a Recaptcha.
   `<div class="g-recaptcha" data-sitekey="some sitekey" data-s="THIS_TOKEN"></div>`

Changed
#######

- Fixed deprecated method `report_incorrect`. 
  You should currently use `report_incorrect_image` instead already.

0.6.0 - 2020-04-13
------------------

Added
#####

- Added custom timeout for ``createTaskSmee``.
  Use as ``client.createTaskSmee(task, timeout=5*60)``.
  Default timeout is 5 minutes.
- Added ``squarenet_validator`` for usage with thread pool
  for concurrent execution

Changed
#######

- Default 5 seconds timeout apply to all API request.

0.5.1 - 2020-03-31
------------------

Changed
#######

- Fix import of package

0.5.0 - 2020-03-30
------------------

Added
#####

- Added ``HCaptchaTaskProxyless`` and ``HCaptchaTask`` for
  support hCaptcha_ . See ``examples/hcaptcha_request.py`` for detailed 
  usage example.
- Added ``SquareNetTask``. See ``examples/squarenet.py`` for detailed
  usage example.
- Added ``Job.report_incorrect_recaptcha`` and ``Job.report_incorrect_image`` .

Changed
#######

- Exposed ``FunCaptchaProxylessTask`` as ``python_anticaptcha.FunCaptchaProxylessTask``
- Exposed ``CustomCaptchaTask`` as ``python_anticaptcha.CustomCaptchaTask``
- Formated code via Black
- Move constant monitoring to GitHub Actions
- Deprecated ``Job.report_incorrect``. Use ``report_incorrect_image`` instead.

0.4.2 - 2019-10-27
------------------

Added
#####

- Added example ``remote_image.py``

Changed
#######

- Switch CI from TravisCI to GitHub Actions
- Automate PyPI releases
- Use ``use_scm_version`` for versioning
- Drop ``use_2to3`` in ``setup.py``

0.4.1 - 2019-07-09
------------------

Added
#####

- Added ``python_anticaptcha.__version__`` to provide version signature (see PEP396)

Changed
#######

- ``python_anticaptcha.AnticaptchaClient.createTaskSmee`` use shared session & keep connection.

0.4.0 - 2019-06-28
------------------

Added
#####

- Added ``python_anticaptcha.AnticaptchaClient.createTaskSmee`` to receive responses without polling
	The method, which is based on the callback result of captcha / task factory to Smee.io,
	which immediately transfers it to library. Allows to significantly shorten the waiting time
	for a response and to reduce load the network connection.
	The method is in beta and the way it works may change. All comments are welcome.
- Recaptcha V3 is now officially supported by Anti-Captcha. Added ``python_anticaptcha.RecaptchaV3TaskProxyless``.

0.3.2 - 2018-10-17
------------------

Added
#####

- Added support for ``IsInvisible`` flag in ``NoCaptchaTaskProxylessTask`` and ``NoCaptchaTask``

0.3.1 - 2018-03-18
------------------

Changed
#######

- Replaced ``python_anticaptcha.AnticatpchaException`` to ``python_anticaptcha.AnticaptchaException`` due typo

Added
#####

- Added ``python_anticaptcha.exceptions.AnticatpchaException``
- Added docs about error handling

Removed
#######

- Deprecated ``python_anticaptcha.exceptions.AnticatpchaException``

.. _hCaptcha: https://www.hcaptcha.com/
