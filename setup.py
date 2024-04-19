from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        "fin/containers/tuple.pyx",
        "fin/mathx.pyx",
        "fin/mem.pyx",
        "fin/model/kellyx.pyx",
        "fin/model/solvers/particle.pyx",
        "fin/model/solvers/random.pyx",
        "fin/model/solvers/solver.pyx",
        "fin/seq/coltypes.pyx",
        "fin/seq/column.pyx",
        "fin/seq/fc/statx.pyx",
        "fin/seq/fc/tix.pyx",
        "fin/seq/serie.pyx",
        "fin/seq/smachine.pyx",
        "fin/tuplex.pyx",
        "fin/utils/ternary.pyx",

        "tests/fin/tuplex.pyx",
        "tests/fin/utils/ternary.pyx",
        ],
        annotate=True,
        compiler_directives={'language_level' : "3"},
    )
)
