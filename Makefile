
PYPI_REPO=https://test.pypi.org/legacy/


.PHONY: dist
dist:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

.PHONY: dist
clean:
	rm -rf build dist pybinmap.egg-info

.PHONY: publish
publish: clean dist
	twine upload --repository-url ${PYPI_REPO} dist/*
