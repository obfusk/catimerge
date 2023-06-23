SHELL     := /bin/bash
PYTHON    ?= python3

export PYTHONWARNINGS := default

.PHONY: all install test lint lint-extra clean cleanup

all:

install:
	$(PYTHON) -mpip install -e .

test: lint lint-extra

lint:
	flake8 catimerge/__init__.py
	pylint catimerge/__init__.py

lint-extra:
	mypy --strict --disallow-any-unimported catimerge/__init__.py

clean: cleanup
	rm -fr catimerge.egg-info/

cleanup:
	find -name '*~' -delete -print
	rm -fr catimerge/__pycache__/ .mypy_cache/
	rm -fr build/ dist/
	rm -fr .coverage htmlcov/
	rm -fr .tmp/

.PHONY: _package _publish

_package:
	SOURCE_DATE_EPOCH="$$( git log -1 --pretty=%ct )" \
	  $(PYTHON) setup.py sdist bdist_wheel
	twine check dist/*

_publish: cleanup _package
	read -r -p "Are you sure? "; \
	[[ "$$REPLY" == [Yy]* ]] && twine upload dist/*
