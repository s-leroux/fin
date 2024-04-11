from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        "fin/mathx.pyx",
        "fin/model/kellyx.pyx",
        "fin/model/solvers/particle.pyx",
        "fin/model/solvers/random.pyx",
        "fin/model/solvers/solver.pyx",
        "fin/seq/column.pyx",
        "fin/seq/fc/funcx.pyx",
        "fin/seq/fc/statx.pyx",
        "fin/seq/fc/tix.pyx",
        "fin/seq/serie.pyx",
        "fin/tuplex.pyx",

        "tests/fin/seq/fc/functor.pyx",
        "tests/fin/tuplex.pyx",
        ],
        annotate=True,
        compiler_directives={'language_level' : "3"},
    )
)
