import os

import numpy as np
from setuptools import find_packages
from setuptools import setup
from Cython.Build import cythonize


def get_version() -> str:

    with open(os.path.join("fastcontour", "__init__.py")) as file:
        for line in file.readlines():
            if line.startswith("__version__"):
                version = line.strip().split(" = ")[1]
                return version.replace('"', "")
        else:
            raise RuntimeError("Didn't manage to find version string.")


setup(
    name="fastcontour",
    version=get_version(),
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
