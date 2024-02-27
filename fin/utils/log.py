import os
import sys
import traceback

from fin.utils import termcap

# ======================================================================
# Logging facilities
# ======================================================================
class Logging:
    def __init__(self, ostream, *, tc=None, log_level=None):
        if tc is None:
            self._termcap = termcap.TermCap.for_stream(ostream)
        else:
            self._termcap = tc

        self._ostream = ostream
        if log_level is None:
            self._log_level = 1
            self.init_log_level()
        else:
            self._log_level = int(log_level)

    def init_log_level(self):
        ll = os.environ.get("FIN_DEBUG", "1")
        try:
            self._log_level = int(ll)
        except ValueError:
            self.warn("FIN_DEBUG should be an int")

    def callsite(self):
        tb = traceback.extract_stack(limit=3)
        frame = tb[0]
        return f"{frame.filename}:{frame.lineno}"

    def error(self, *args):
        print(self._termcap.red("E:"+self.callsite()), *args, file=self._ostream, flush=True)

    def warn(self, *args):
        if self._log_level > 0:
            print(self._termcap.yellow("W:"+self.callsite()), *args, file=self._ostream, flush=True)

    def info(self, *args):
        if self._log_level > 1:
            print(self._termcap.green("I:"+self.callsite()), *args, file=self._ostream, flush=True)

    def debug(self, *args):
        if self._log_level > 2:
            print(self._termcap.green("D:"+self.callsite()), *args, file=self._ostream, flush=True)

console = Logging(sys.stderr)
