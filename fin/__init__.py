__version_info__ = (0, 3, 0)
__version__ = '.'.join(map(str,__version_info__))

__history__ = {
    "0.3.0":
    """ Introduce three-state logical columns and a temptative back-tester.
    """,
    "0.2.3":
    """ Rewrite of some internal helpers.

        New interpreter for s_expr.
        Columns now use the custom container `fin.containers.Tuple` instead of standard `tuple`.
    """,
    "0.2.2":
    """ All serie predicates are implemented.

        - create()
        - select()
        - extend()
        - sort_by()
        - group_by()
        - where()

        See docs/snippets/snippet_counting_001.py for an example.

    """,
    "0.2.1":
    """ Add complex models and multi-variable solver.
    """,
    "0.2.0":
    """ Complete rewrite of the fin/seq module.
    """,
    "0.1.0":
    """ First versioned package.
    """,
}
