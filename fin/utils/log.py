import sys

from fin.utils import termcap

# ======================================================================
# Logging facilities
# ======================================================================
class Logging:
    def __init__(self, ostream, tc=None):
        if tc is None:
            if ostream.isatty():
                self._termcap = termcap.ANSITerminalTermCap()
            else:
                self._termcap = termcap.TermCap()
        else:
            self._termcap = tc

        self._ostream = ostream

    def error(self, code, *args):
        code = str(code)
        assert len(code) == 6, "Code must be a 6-character string"

        print(self._termcap.red("E"+code), *args, file=self._ostream, flush=True)

    def warn(self, code, *args):
        code = str(code)
        assert len(code) == 6, "Code must be a 6-character string"

        print(self._termcap.yellow("W"+code), *args, file=self._ostream, flush=True)

    def info(self, code, *args):
        code = str(code)
        assert len(code) == 6, "Code must be a 6-character string"

        print(self._termcap.green("I"+code), *args, file=self._ostream, flush=True)

    def debug(self, *args):
        print(self._termcap.green("DEBUG: "), *args, file=self._ostream, flush=True)

console = Logging(sys.stderr)
