import os
from collections import OrderedDict
from unittest import TestCase, skipIf

from python_anticaptcha import TextInput, Select, AnticaptchaClient
from python_anticaptcha.tasks import CustomCaptchaTask, \
    NoCaptchaTaskProxylessTask


class CustomCaptchaTaskTestCase(TestCase):
    def test_serialize(self):
        form = OrderedDict()
        form['dot_count'] = TextInput(label="Dot count", labelHint="Enter the number of dots.")
        form['dot_color'] = Select(label="Dot color", labelHint="Select the color of dots.",
                                   choices=[('red', "Red"),
                                            ('blue', "Blue"),
                                            ('green', "Green")])
        form['license_plate'] = {
            "label": "Number",
            "labelHint": False,
            "contentType": False,
            "inputType": "text",
            "inputOptions": {
                "width": "100",
                "placeHolder": "Enter a letters and number without spaces"
            }
        }
        task = CustomCaptchaTask(imageUrl="https://s.jawne.info.pl/dot_img",
                                 assignment="Count the dots and indicate their color.",
                                 form=form)
        expected_result = {
            'type': 'CustomCaptchaTask',
            'assignment': 'Count the dots and indicate their color.',
            'imageUrl': 'https://s.jawne.info.pl/dot_img',
            'forms': [
                {'labelHint': 'Enter the number of dots.',
                 'inputType': 'text',
                 'inputOptions': {},
                 'name': 'dot_count',
                 'label': 'Dot count'},
                {'labelHint': 'Select the color of dots.',
                 'inputType': 'select',
                 'inputOptions': [{'caption': 'Red', 'value': 'red'},
                                  {'caption': 'Blue', 'value': 'blue'},
                                  {'caption': 'Green', 'value': 'green'}],
                 'name': 'dot_color',
                 'label': 'Dot color'},
                {"label": "Number",
                 "labelHint": False,
                 "contentType": False,
                 "name": "license_plate",
                 "inputType": "text",
                 "inputOptions": {
                     "width": "100",
                     "placeHolder": "Enter a letters and number without spaces"
                 }}
            ]
        }
        self.assertSequenceEqual(sorted(task.serialize().keys()), sorted(expected_result.keys()))
        for result, expected in zip(task.serialize()['forms'], expected_result['forms']):
            self.assertSequenceEqual(sorted(result.keys()), sorted(expected.keys()))
            self.assertDictEqual(result, expected)
        self.assertSequenceEqual(task.serialize()['forms'], expected_result['forms'])
        self.assertDictEqual(task.serialize(), expected_result)


@skipIf('KEY' not in os.environ, 'Missing KEY environment variable. Unable to connect Anti-captcha.com')
# @skipIf('TRAVIS' in os.environ, 'Skip heavy tests in TravisCI.')
class TestNoCaptchaTask(TestCase):
    def test_invisible_captcha(self):
        client = AnticaptchaClient(os.environ['KEY'])
        task = NoCaptchaTaskProxylessTask(
            website_url='https://losangeles.craigslist.org/lac/kid/d/housekeeper-sitting-pet-care/6720136191.html',
            website_key='6Lc-0DYUAAAAAOPM3RGobCfKjIE5STmzvZfHbbNx',
        )
        job = client.createTask(task)
        job.join()
        self.assertIsInstance(job.get_solution_response(), (str, unicode))