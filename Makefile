.PHONY: lint fmt build

build:
	python setup.py sdist bdist_wheel

clean:
	rm -r build

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./
