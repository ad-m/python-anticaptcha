from setuptools import setup
from codecs import open
from os import path, system
import sys

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

version = '0.3.2'

tests_deps = [
    'nose',
    'retry'
]

extras = {
    'tests': tests_deps,
    'docs': 'sphinx'
}

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        raise ImportError("Fix: pip install wheel")
    system('python setup.py sdist bdist_wheel --universal upload')
    print("You probably want to also tag the version now:")
    print("  git push --tags")
    sys.exit()

setup(
    name='python-anticaptcha',
    version=version,
    description='Client library for solve captchas with Anticaptcha.com support.',
    long_description=long_description,
    url='https://github.com/ad-m/python-anticaptcha',
    author='Adam Dobrawy',
    author_email='anticaptcha@jawnosc.tk',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    use_2to3=True,
    keywords='recaptcha captcha development',
    packages=['python_anticaptcha'],
    install_requires=['requests', 'six'],
    tests_require=tests_deps,
    extras_require=extras
)
