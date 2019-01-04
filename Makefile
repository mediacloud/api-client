PYLINT := env PYTHONPATH=$(PYTHONPATH) pylint

install:
	pip install -r requirements.txt

lint:
	$(PYLINT) mediacloud

test:
	python test.py

build-release:
	find . -name '.DS_Store' -type f -delete
	python setup.py sdist bdist_wheel

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release:
	twine upload dist/*
