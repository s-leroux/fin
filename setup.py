from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        "fin/mathx.pyx",
        "fin/model/kellyx.pyx",
        "fin/seq/algox.pyx",
        "fin/seq/column.pyx",
        ], annotate=True)
)
