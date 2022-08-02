build:
	python setup.py build_ext --build-lib .

install:
	pip install -U .

inspect:
	cython -a -3 --cplus fastcontour/_interpolation.pyx
	xdg-open fastcontour/_interpolation.html
