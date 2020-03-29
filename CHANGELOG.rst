Changelog
=========

0.5.0 - 2020-03-29
------------------

Added
#####

- Added ```HCaptchaTaskProxyless``` and ```HCaptchaTaskProxyless``` for support `hCaptcha
<https://www.hcaptcha.com/>`_ . See ```examples/hcaptcha_request.py``` for detailed usage example.
- Added ```SquareNetTask```. See ```examples/squarenet.py``` for detailed usage example.

Changed
#######

- Expose ```FunCaptchaProxylessTask``` as ```python_anticaptcha.FunCaptchaProxylessTask```
- Expose ```CustomCaptchaTask``` as ```python_anticaptcha.CustomCaptchaTask```
- Format code via Black

0.4.2 - 2019-10-27
------------------

Added
#####

- Added example ```remote_image.py```

Changed
#######

- Switch CI from TravisCI to GitHub Actions
- Automate PyPI releases
- Use ```use_scm_version``` for versioning
- Drop ```use_2to3``` in ```setup.py```

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
