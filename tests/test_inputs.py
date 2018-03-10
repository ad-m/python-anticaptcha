from unittest import TestCase

from python_anticaptcha.fields import SimpleText, Image, WebLink, Textarea, Checkbox, Select, Radio, ImageUpload, \
    TextInput


class SimpleTextTestCase(TestCase):
    def test_serialize(self):
        form = SimpleText(label="name", labelHint="subtitle", content="content")

        self.assertEqual(form.serialize(), {
            "label": "name",
            "labelHint": "subtitle",
            "contentType": "text",
            "content": "content"
        })


class ImageTestCase(TestCase):
    def test_serialize(self):
        form = Image(label="title", labelHint="subtitle", imageUrl="https://s.jawne.info.pl/dot_img")

        self.assertEqual(form.serialize(), {
            "label": "title",
            "labelHint": "subtitle",
            "contentType": "image",
            "content": "https://s.jawne.info.pl/dot_img"
        })


class WebLinkTestCase(TestCase):
    def test_serialize(self):
        form = WebLink(label="title", labelHint="subtitle", linkText="text", linkUrl="https://s.jawne.info.pl/dot_img")

        self.assertEqual(form.serialize(name="link"), {
            "label": "title",
            "labelHint": "subtitle",
            "contentType": "link",
            "content": {
                "url": "https://s.jawne.info.pl/dot_img",
                "text": "text"
            }
        })


class TextInputTestCase(TestCase):
    def test_serialize(self):
        form = TextInput(label="title", labelHint="subtitle", placeHolder="hint", width=50)

        self.assertDictEqual(form.serialize(name="name", ), {
        "label": "title",
        "labelHint": "subtitle",
        "name": "name",
        "inputType": "text",
        "inputOptions": {
            "width": "50",
            "placeHolder": "hint"
        }
    }
)

class TextareaTestCase(TestCase):
    def test_serialize(self):
        form = Textarea(label="title", labelHint="subtitle", width=50, rows=25, placeHolder="hint")
        self.assertEqual(form.serialize(name="name"), {
            "label": "title",
            "labelHint": "subtitle",
            "name": "name",
            "inputType": "textarea",
            "inputOptions": {
                "width": "50",
                "rows": "25",
                "placeHolder": "hint"
            }
        })


class CheckboxTestCase(TestCase):
    def test_serialize(self):
        form = Checkbox(label="title", labelHint="subtitle", text="checkbox")
        self.assertEqual(form.serialize(name="name"), {
            "label": "title",
            "labelHint": "subtitle",
            "name": "name",
            "inputType": "checkbox",
            "inputOptions": {
                "label": "checkbox"
            }
        })


class SelectTestCase(TestCase):
    def test_serialize(self):
        form = Select(label="title", labelHint="subtitle", choices=[('value', 'caption'), ])
        self.assertEqual(form.serialize(name="name"), {
            "label": "title",
            "labelHint": "subtitle",
            "name": "name",
            "inputType": "select",
            "inputOptions": [
                {
                    "value": "value",
                    "caption": "caption"
                }
            ]
        })


class RadioTestCase(TestCase):
    def test_serialize(self):
        form = Radio(label="title", labelHint="subtitle", choices=[('value', 'caption'), ])
        self.assertEqual(form.serialize(name="name"), {
            "label": "title",
            "labelHint": "subtitle",
            "name": "name",
            "inputType": "radio",
            "inputOptions": [
                {
                    "value": "value",
                    "caption": "caption"
                }
            ]
        })


class ImageUploadTestCase(TestCase):
    def test_serialize(self):
        form = ImageUpload(label="title", labelHint="subtitle")
        self.assertEqual(form.serialize(name="name"), {
            "label": "title",
            "labelHint": "subtitle",
            "name": "name",
            "inputType": "imageUpload"
        })
