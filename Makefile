.PHONY: build
build:
	pip install wheel numpy Cython
	python setup.py build_ext --build-lib .

install:
	pip install wheel numpy Cython
	python setup.py bdist_wheel
	pip install -U dist/*.whl

inspect:
	cython -a -3 --cplus fastcontour/_interpolation.pyx
	xdg-open fastcontour/_interpolation.html
