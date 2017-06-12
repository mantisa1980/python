from distutils.core import setup
from Cython.Build import cythonize

setup(
  ext_modules = cythonize(["lib/mylib.pyx", "lib/mymath.pyx"]),
)
