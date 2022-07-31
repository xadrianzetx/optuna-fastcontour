import os

import numpy as np
from setuptools import find_packages
from setuptools import setup
from Cython.Build import cythonize


setup(
    name="fastcontour",
    version="0.1.0",
    author="Adrian Zuber",
    url="https://github.com/xadrianzetx/optuna-fastcontour",
    packages=find_packages(exclude=("tests")),
    ext_modules=cythonize([os.path.join("fastcontour", ext) for ext in ["*.pyx", "*.pxd"]]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.7",
    install_requires=["optuna @ git+https://github.com/optuna/optuna.git", "matplotlib"],
    extras_require={"test": ["pytest"]},
    include_dirs=[np.get_include()],
)
