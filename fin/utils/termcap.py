"""
Rudimentary terminal capabilities.

Designed mostly with color output in mind.
"""
# ======================================================================
# Terminal capabilities
# ======================================================================

class TermCap:
    def red(self, s):
        return s

    def yellow(self, s):
        return s

    def green(self, s):
        return s

CSI = "\033["

ANSI_SGR_RESET = "0"
ANSI_SGR_BOLD = "1"
ANSI_SGR_INVERT = "7"

ANSI_3BIT_COLORS = dict(
        black=30,
        red=31,
        green=32,
        yellow=33,
        blue=34,
        magenta=35,
        cyan=36,
        white=37,
        bright_black=30,
        bright_red=31,
        bright_green=32,
        bright_yellow=33,
        bright_blue=34,
        bright_magenta=35,
        bright_cyan=36,
        bright_white=37,
        )

class ANSITerminalTermCap(TermCap):
    def red(self, s):
        return self.sgr(bold=True, fgcolor="red") + s + self.sgr(reset=True)

    def yellow(self, s):
        return self.sgr(bold=True, fgcolor="yellow") + s + self.sgr(reset=True)

    def green(self, s):
        return self.sgr(bold=True, fgcolor="green") + s + self.sgr(reset=True)

    def sgr(self, **attrs):
        s = []

        if attrs.get("reset"):
            s.append(ANSI_SGR_RESET)

        fgcolor = attrs.get("fgcolor", None)
        if fgcolor:
            s.append(str(ANSI_3BIT_COLORS[fgcolor]))

        if attrs.get("bold"):
            s.append(ANSI_SGR_BOLD)

        if attrs.get("invert"):
            s.append(ANSI_SGR_INVERT)

        return CSI + ";".join(s) + "m"
