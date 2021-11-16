python-package:
	${RM} -f dist/*
	python3 -m build

pypi:	python-package test
	twine upload dist/*

test:	tests
tests:
	flake8
	tox

.PHONY: python-package pypi tests test
