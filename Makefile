.PHONY: clean clean-pyc clean-build init test deps pretty version docs dist test-release release install

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
	$(MAKE) -C docs clean

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
	pip install -q -r requirements-dev.txt

test: init
	python -m unittest

deps:
	source ~/virtualenvs/bidfx-api/bin/activate
	pip freeze | xargs pip uninstall -y
	pip install .
	echo "to exit the virtual env type: deactivate"

pretty:
	black .

version:
	bumpversion minor

docs:
	$(MAKE) -C docs clean html
	$(BROWSER) docs/build/html/index.html

dist: clean pretty test docs
	python setup.py sdist
	python setup.py bdist_wheel

test-release: dist
	twine upload --repository testpypi dist/*

release: dist
	twine upload dist/*

install: clean
	python setup.py install
