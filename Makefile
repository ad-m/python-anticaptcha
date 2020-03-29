.PHONY: lint fmt build docs install test

build:
	python setup.py sdist bdist_wheel

install: install_test install_docs install_pkg
	
install_test:
	pip install .[tests]

install_docs:
	pip install .[docs]

install_pkg:
	python -m pip install --upgrade pip wheel
	pip install .

gecko:
	wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
	mkdir geckodriver
	tar -xzf geckodriver-v0.24.0-linux64.tar.gz -C geckodriver
	rm geckodriver-v0.24.0-linux64.tar.gz

test:
	# nosetests tests -v --with-coverage --cover-package=python_anticaptcha --processes=8
	PATH=$$PATH:$$PWD/geckodriver nosetests tests --verbosity=3 --processes=8 --process-timeout=1200

clean:
	rm -r build geckodriver

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./

docs:
	sphinx-build -W docs /dev/shm/sphinx