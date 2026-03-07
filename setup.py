from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


tests_deps = ["retry", "pytest", "selenium"]

extras = {"tests": tests_deps, "docs": "sphinx"}

setup(
    name="python-anticaptcha",
    description="Client library for solve captchas with Anticaptcha.com support.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ad-m/python-anticaptcha",
    author="Adam Dobrawy",
    author_email="naczelnik@jawne.info.pl",
    license="MIT",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    use_scm_version=True,
    setup_requires=["setuptools_scm", "wheel"],
    keywords="recaptcha captcha development",
    packages=["python_anticaptcha"],
    install_requires=["requests"],
    extras_require=extras,
)
