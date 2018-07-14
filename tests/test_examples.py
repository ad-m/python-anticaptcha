# -*- coding: utf-8 -*-
from unittest import TestCase, skipIf
from retry import retry

import os

from python_anticaptcha import AnticatpchaException


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
@skipIf('TRAVIS' in os.environ, 'Skip heavy tests in TravisCI.')
class CustomDotTestCase(TestCase):

    # @retry(tries=3)  # For unknown reasons, workers are not always able to count correctly. ¯\_(ツ)_/¯
    def test_process_dot(self):
        from examples import custom_dot
        self.assertEqual(custom_dot.process(custom_dot.URL), custom_dot.EXPECTED_RESULT)


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
@skipIf('TRAVIS' in os.environ, 'Skip heavy tests in TravisCI.')
class CustomModerationTestCase(TestCase):
    def test_process_bulk_iter(self):
        from examples import custom_moderation
        self.assertSequenceEqual(sorted(list(custom_moderation.process_bulk_iter(custom_moderation.URLS))),
                                 sorted(zip(custom_moderation.URLS, custom_moderation.RESULTS)))

    def test_process_bulk(self):
        from examples import custom_moderation
        self.assertEqual(custom_moderation.process_bulk(custom_moderation.URLS), custom_moderation.RESULTS)


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
@skipIf('TRAVIS' in os.environ, 'Skip heavy tests in TravisCI.')
@skipIf('PROXY_URL' not in os.environ, 'Missing PROXY_URL environment variable')
class FuncaptchaTestCase(TestCase):
    # @retry(AnticatpchaException, tries=3)  # CI Proxy is unstable. Occasionally fails, so I repeat my attempt to have others selected.
    def test_funcaptcha(self):
        from examples import funcaptcha
        self.assertTrue(funcaptcha.process())


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
class RecaptchaTestCase(TestCase):
    def test_process(self):
        from examples import recaptcha
        self.assertIn('Verification Success... Hooray!', recaptcha.process())


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
class TextTestCase(TestCase):
    def test_process(self):
        from examples import text
        self.assertEqual(text.process(text.IMAGE).lower(), text.EXPECTED_RESULT.lower())
