.PHONY: lint fmt build docs

build:
	python setup.py sdist bdist_wheel

clean:
	rm -r build

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./

docs:
	sphinx-build -W docs /dev/shm/sphinx