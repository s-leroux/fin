
class Underdefined(Exception):
    def __init__(self, params, *args):
        message = "Too many missing parameters: {}".format(params)
        super(Exception, self).__init__(message)

        self._params = params
