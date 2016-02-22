.PHONY: build clean upload test-upload

default: build

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build dist *.egg-info

upload: clean build
	twine upload dist/*

test-upload: clean build
	twine upload -r pypitest dist/*
