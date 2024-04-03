from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        "test.pyx",

        "fin/mathx.pyx",
        "fin/model/kellyx.pyx",
        "fin/seq/column.pyx",
        "fin/seq/fc/functorx.pyx",
        "fin/seq/fc/statisticx.pyx",
        "fin/seq/fc/tix.pyx",
        "fin/seq/serie.pyx",

        "tests/fin/seq/fc/functor.pyx",
        ],
        annotate=True,
        compiler_directives={'language_level' : "3"},
    )
)
