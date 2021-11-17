python-package:
	python3 -m build

# With additional README (ugly hack; better solutions out there?)
distribution-package:	python-package
	${RM} -rf dist/* build/*
	mkdir -p build/lib/fake_super
	cp README.md build/lib/fake_super/
	python3 -m build

pypi:	distribution-package test
	twine upload dist/*

test:	tests
tests:
	flake8
	cd src && mypy -p fake_super
	PYTHONPATH= tox

.PHONY: python-package pypi tests test
