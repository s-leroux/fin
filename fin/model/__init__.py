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
from inspect import signature, Parameter

def Model(eq, params={}):
    """
    A mathematical model whose parameters are interdependant.

    The model is defined by an ``equilibrium function``. That is a function 
    which returns 0 if the model is at equilibrium. The model's variables
    are infered from the parameters of the equilibrium function.

    This functions return a new class that you can use to create instances
    of this model.

    On instances, you can query the individual parameter values using the 
    subscript syntax.  When a parameter is not set, the model first try to
    infer its values from a user specified function or using the generic solver.
    """
    # ------------------------------------------------------------------
    # _Model class
    # ------------------------------------------------------------------
    class _Model:
        def __init__(self, values):
            if len(model) - len(values) > 1:
                raise Underdefined(model, values)
            self._values = values.copy()

        def adjust(self, x, conditions):
            """
            Recalculate the "x" parameter under the given conditions.
            Return a new instance of the receiver's class.
            """
            new_values = { k: self[k] for k in model.keys() if k != x and k not in conditions }
            new_values.update(conditions);

            return self.clone(new_values)

        def clone(self, new_values):
            return type(self)(new_values)

        def __getitem__(self, name):
            sentinel = object()
            value = self._values.get(name, sentinel)
            if value is sentinel:
                # Not found!
                value = self._values[name] = model[name](**self._values)

            return value

        def __repr__(self):
            T = type(self)
            return "{}.{}({})".format(T.__module__, T.__qualname__, self._values)
    # ------------------------------------------------------------------
    # End of _Model class
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Default solver
    # ------------------------------------------------------------------
    def solver(pname, start=-fin.math.HUGE, end=fin.math.HUGE):
        def _solver(**params):
            # Default resolution forwarded to the generic solver
            return fin.math.solve(eq,
                        pname,
                        start,
                        end,
                        params
                   )
        return _solver
    # ------------------------------------------------------------------
    # End of default solver
    # ------------------------------------------------------------------

    # For compatibility with previous implementations
    if type(params) == tuple:
        params = {k: None for k in params}

    pnames = [ k for k, v in signature(eq).parameters.items() if v.kind == Parameter.POSITIONAL_OR_KEYWORD ]
    model = {}
    for k in pnames:
        param = params.get(k)
        # it is either a callable, None or a 2uple
        if param is None:
            param = solver(k)
        elif type(param) == tuple:
            param = solver(k, *param)

        model[k] = param

    return _Model

