CHROMEDRIVER_VERSION=99.0.4844.17
CHROMEDRIVER_DIR=${PWD}/geckodriver

.PHONY: lint fmt build docs install test gecko

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
	mkdir -p ${CHROMEDRIVER_DIR}
	wget -q -P ${CHROMEDRIVER_DIR} "http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
	unzip ${CHROMEDRIVER_DIR}/chromedriver* -d ${CHROMEDRIVER_DIR}
	rm ${CHROMEDRIVER_DIR}/chromedriver_linux64.zip

test:
	PATH=$$PWD/geckodriver:$$PATH nose2 --verbose

clean:
	rm -r build geckodriver

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./

docs:
	sphinx-build -W docs /dev/shm/sphinx