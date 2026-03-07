CHROMEDRIVER_VERSION=99.0.4844.17
CHROMEDRIVER_DIR=${PWD}/chromedriver

.PHONY: lint fmt build docs install test test_e2e chromedriver

build:
	python -m build

install: install_test install_docs install_pkg
	
install_test:
	pip install .[tests]

install_docs:
	pip install .[docs]

install_pkg:
	python -m pip install --upgrade pip wheel
	pip install .

chromedriver:
	mkdir -p ${CHROMEDRIVER_DIR}
	wget -q -P ${CHROMEDRIVER_DIR} "http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
	unzip ${CHROMEDRIVER_DIR}/chromedriver* -d ${CHROMEDRIVER_DIR}
	rm ${CHROMEDRIVER_DIR}/chromedriver_linux64.zip

test:
	pytest

test_e2e:
	PATH=$$PWD/chromedriver:$$PATH pytest -m e2e --override-ini="addopts="

clean:
	rm -r build chromedriver

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./

docs:
	sphinx-build -W docs /dev/shm/sphinx