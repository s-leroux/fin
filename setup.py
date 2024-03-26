from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        "fin/mathx.pyx",
        "fin/model/kellyx.pyx",
        "fin/seq/algox.pyx",
        "fin/seq/column.pyx",
        "fin/seq2/column.pyx",
        "fin/seq2/serie.pyx",
        "fin/seq2/fc/functorx.pyx",
        "fin/seq2/fc/statisticx.pyx",

        "tests/fin/seq2/fc/functor.pyx",
        ],
        annotate=True,
        compiler_directives={'language_level' : "3"},
    )
)
