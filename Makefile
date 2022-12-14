BUILD_DEPENDENCIES := $(shell awk '/build-system/{getline; print}' pyproject.toml | awk -F'[][]' '{print $$2}' | sed 's/"//g;s/,//g')

.PHONY: build
build:
	pip install $(BUILD_DEPENDENCIES)
	python setup.py build_ext --build-lib .

install:
	pip install -U .

inspect:
	cython -a -3 --cplus fastcontour/*.pyx
	ls fastcontour/*.html | xargs -n 1 python -m webbrowser
