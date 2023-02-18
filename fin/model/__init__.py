import fin.math

class Underdefined(Exception):
    def __init__(self, params, *args):
        message = "Too many missing parameters: {}".format(params)
        super(Exception, self).__init__(message)

        self._params = params

class Model:
    def __init__(self, fct, pnames, params):
        a = -fin.math.HUGE
        b = fin.math.HUGE

        self._fct = fct
        self._params = {}
        missing = []
        for pname in pnames:
            pvalue = self._params[pname] = params.get(pname)
            if pvalue is None:
                missing.append(pname)
            else:
                try:
                    a, b = pvalue
                    missing.append(pname)
                except:
                    pass

        if len(missing) > 1:
            raise Underdefined(missing)

        if len(missing) == 1:
            pname = missing[0]
            self._params[pname] = fin.math.solve(
                    self._fct,
                    pname,
                    a,
                    b,
                    self._params
            )

    def adjust(self, x, conditions):
        """
        Recalculate the "x" parameter under the given conditions.
        Return a new instance of the receiver's class.
        """
        new_params = self._params.copy()
        new_params.update(conditions)
        new_params.pop(x, None)

        return self.clone(new_params)

    def clone(self, new_params):
        return type(self)(new_params)

    def __getitem__(self, name):
        return self._params[name]

    def __repr__(self):
        T = type(self)
        return "{}.{}({})".format(T.__module__, T.__qualname__, self._params)

