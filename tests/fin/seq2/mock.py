# ======================================================================
# Mock series
# ======================================================================
class SerieMock:
    def __init__(self, **kwargs):
        self._properties = kwargs

    def __getattr__(self, name):
        # Emulate read-only properties
        return self._properties[name]

