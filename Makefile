.PHONY: lint fmt

lint:
	docker run --rm -v /$$(pwd):/apps alpine/flake8 ./
	docker run --rm -v /$$(pwd):/data cytopia/black --check ./

fmt:
	docker run --rm -v /$$(pwd):/data cytopia/black ./
