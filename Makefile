PYLINT := env PYTHONPATH=$(PYTHONPATH) pylint

install:
	pip install -e .[dev]

lint:
	$(PYLINT) mediacloud

test:
	pytest

build-release:
	find . -name '.DS_Store' -type f -delete
	python setup.py sdist

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release:
	twine upload dist/*
