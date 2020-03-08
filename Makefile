.PHONY: clean-pyc clean-build docs clean init test deps version pretty

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"


clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

init:
	pip install -q -r requirements.txt

test: init
	python -m unittest

deps:
	source ~/virtualenvs/bidfx-api/bin/activate
	pip freeze | xargs pip uninstall -y
	pip install .
	echo "to exit the virtual env type: deactivate"

pretty:
	black .

version: pretty
	bumpversion minor

docs:
	$(MAKE) -C docs clean html
	$(BROWSER) docs/build/html/index.html

release: clean test docs
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean test docs
	python setup.py sdist
	python setup.py bdist_wheel

install: clean
	python setup.py install
