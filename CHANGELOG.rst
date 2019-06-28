Changelog
=========

0.4.0 - 2019-06-28
------------------

Added
#####

- Added ``python_anticaptcha.AnticaptchaClient.createTaskStream`` to receive responses without polling
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
