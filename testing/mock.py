import inspect

class MockFunction:
    def __init__(self, delegate):
        self.delegate = delegate

        self.called = False
        self.call_count = 0
        self.call_args = None
        self.call_args_list = []

        self.signature = inspect.signature(delegate)

    def log_call(self, args, kwargs):
        self.called = True
        self.call_count += 1
        self.call_args = self.signature.bind(*args, **kwargs).arguments
        self.call_args_list.append(self.call_args)

    def __call__(self, *args, **kwargs):
        self.log_call(args, kwargs)
        return self.delegate(*args, **kwargs)

