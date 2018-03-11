Custom fields
=============

Python-Anticaptcha since 0.3.0 supports task type ```CustomCaptchaTask``. It allows collects arbitrary description of image.

This type of tasks is suitable for use when you need to describe what is on an image and you need workers to fill a custom form about this.

Examples:

* Build ML dataset
* Read letters and numbers from a car license plate
* Find a phone number on a commercial
* Reading data from the invoice scan
* Complete task like "count monkeys on a picture"
* etc.

If your case does not fit in such a flow, and yet you need a human factor for many repetitive tasks - `create an issue`_,
use `Gitter`_ or contact privately.

.. _create an issue: https://github.com/ad-m/python-anticaptcha/issues/new
.. _Gitter: https://gitter.im/python-anticaptcha/Lobby

At the beginning you need to initialize the `Anti-captcha.com`_ client:

.. code-block:: python

    from python_anticaptcha import AnticaptchaClient
    api_key = 'xxxx'
    client = AnticaptchaClient(api_key)

Then you build the form as dict of fields:

.. code-block:: python

    from collections import OrderedDict
    from python_anticaptcha.fields import TextInput, Select

    form = OrderedDict()
    form['dot_count'] = TextInput(label="Dot count",
                                  labelHint="Enter the number of dots.")
    form['dot_color'] = Select(label="Dot color",
                               labelHint="Select the color of dots.",
                               choices=[('red', "Red"),
                                        ('blue', "Blue"),
                                        ('green', "Green")])

The form field key name specifies the name of the answer key.

There is multiple types of form fields, see :ref:`form_fields`.

If they do not meet your expectations - use the JSON structure directly.
You can use the following to build a proper structure:

* use `FormBuilder`_ tool in Anti-Captcha.com clients area.
* code it manually using `Anti-captcha.com documentation`_.

Next to send form & image URL to `Anti-captcha.com`_ and receive answer:

.. code-block:: python

    url = "https://s.jawne.info.pl/dot_img"
    task = CustomCaptchaTask(imageUrl=url,
                             assignment="Count the dots and indicate their color.",
                             form=form)

    job = client.createTask(task)
    job.join()
    answer = job.get_answers()
    print(answer['dot_count'], answer['dot_color'])

.. _Anti-captcha.com: http://getcaptchasolution.com/i1hvnzdymd
.. _FormBuilder: https://anti-captcha.com/clients/factories/directory/formbuilder
.. _Anti-captcha.com documentation: https://anticaptcha.atlassian.net/wiki/spaces/API/pages/41287896/Form+Object
