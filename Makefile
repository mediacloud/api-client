PYLINT := env PYTHONPATH=$(PYTHONPATH) pylint

install:
	pip install -r requirements.pip

lint:
	$(PYLINT) mediacloud

test:
	python test.py

build:
	python setup.py sdist

release:
	python setup.py sdist
	python setup.py sdist upload -r pypitest
	python setup.py sdist upload -r pypi
