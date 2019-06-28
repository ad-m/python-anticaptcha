from collections import OrderedDict
from os import environ

from python_anticaptcha import AnticaptchaClient
from python_anticaptcha.fields import TextInput, Select, Radio
from python_anticaptcha.tasks import CustomCaptchaTask

api_key = environ['KEY']

URL = "https://s.jawne.info.pl/dot_img"
EXPECTED_RESULT = ('7', 'red')

CHOICES = [('red', "Red"),
           ('blue', "Blue"),
           ('green', "Green")]

CHOICES_COUNTRY = [('VE', 'Venezuela'),
                   ('IN', 'India'),
                   ('US', 'United States'),
                   ('MA', 'Morocco'),
                   ('BD', 'Bangladesh'),
                   ('PH', 'Philippines'),
                   ('ID', 'Indonesia'),
                   ('RU', 'Russia'),
                   ('VN', 'Vietnam'),
                   ('UA', 'Ukraine'),
                   ('CA', 'Canada'),
                   ('Other', 'Other')]

CHOICES_GENRE = [('M', 'Male'),
                 ('F', 'Female'),
                 ('O', 'Other')]

form = OrderedDict()
form['dot_count'] = TextInput(label="Dot count", labelHint="Enter the number of dots.")
form['dot_color'] = Select(label="Dot color", labelHint="Select the color of dots.", choices=CHOICES)

form['country'] = Select(label="Your country", labelHint="Select your country of origin", choices=CHOICES_COUNTRY)
form['genre'] = Radio(label="Your genre", labelHint="Select your genre", choices=CHOICES_GENRE)


def process(url):
    client = AnticaptchaClient(api_key)
    task = CustomCaptchaTask(
        imageUrl=url,
        assignment="Count the dots and indicate their color.",
        form=form
    )
    job = client.createTaskSmee(task)
    answer = job.get_answers()
    return answer['dot_count'], answer['dot_color']


if __name__ == '__main__':
    print("ImageUrl: " + URL)
    print("Result: " + str(process(URL)))
    print("Expected: " + str(EXPECTED_RESULT))
