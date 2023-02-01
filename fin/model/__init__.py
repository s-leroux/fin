import fin.math

class Underdefined(Exception):
    def __init__(self, params, *args):
        message = "Too many missing parameters: {}".format(params)
        super(Exception, self).__init__(message)

        self._params = params

class Model:
    def __init__(self, fct, pnames, params):
        self._fct = fct
        self._params = {}
        missing = []
        for pname in pnames:
            pvalue = self._params[pname] = params.get(pname)
            if pvalue is None:
                missing.append(pname)

        if len(missing) > 1:
            raise Underdefined(missing)

        if len(missing) == 1:
            pname = missing[0]
            self._params[pname] = fin.math.solve(
                    self._fct,
                    pname,
                    fin.math.EPSILON,
                    fin.math.HUGE,
                    self._params
            )

    def __getattr__(self, name):
        return self._params[name]

    def __repr__(self):
        T = type(self)
        return "{}.{}({})".format(T.__module__, T.__qualname__, self._params)

