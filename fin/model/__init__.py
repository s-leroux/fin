import fin.math

# ======================================================================
# Exceptions
# ======================================================================
class Underdefined(Exception):
    def __init__(self, expected, actual, *args):
        message = "Too many missing parameters:\nExpected: {}\nActual: {}".format(expected.keys(), actual)
        super(Exception, self).__init__(message)

        self._actual = actual
        self._expected = expected

# ======================================================================
# Model
# ======================================================================
class Model:
    """
    A mathematical model whose parameters are interdependant.

    The model is defined by an ``equilibrium function``. That is a function 
    which returns 0 if the model is at equilibrium.

    You can query the individual parameter values using the subscript syntax.
    When a parameter was not set, the model first try to infer its values
    from a user specified function or using the generic solver.
    """
    def __init__(self, eq, params, values):
        # For compatibility with previous implementations
        if type(params) == tuple:
            params = {k: None for k in params}

        def solver(pname):
            def _solver(**params):
                # Default resolution forwarded to the generic solver
                return fin.math.solve(eq,
                            pname,
                            -fin.math.HUGE,
                            fin.math.HUGE,
                            params
                       )
            return _solver

        if len(params) - len(values) > 1:
            raise Underdefined(params, values)

        self._eq = eq
        self._values = {}
        self._params = {}

        for pname, pvalue in params.items():
            if callable(pvalue):
                self._params[pname] = pvalue
            else:
                self._params[pname] = solver(pname)

        self._values = values.copy()

    def adjust(self, x, conditions):
        """
        Recalculate the "x" parameter under the given conditions.
        Return a new instance of the receiver's class.
        """
        new_values = { k: self[k] for k in self._params.keys() if k != x and k not in conditions }
        new_values.update(conditions);

        return self.clone(new_values)

    def clone(self, new_values):
        return type(self)(new_values)

    def __getitem__(self, name):
        sentinel = object()
        value = self._values.get(name, sentinel)
        if value is sentinel:
            # Not found!
            value = self._values[name] = self._params[name](**self._values)

        return value

    def __repr__(self):
        T = type(self)
        return "{}.{}({})".format(T.__module__, T.__qualname__, self._values)

