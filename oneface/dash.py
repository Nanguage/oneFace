import functools


def app(func=None, **kwargs):
    if func is None:
        return functools.partial(**kwargs)
    return App(func, **kwargs)


class App(object):
    def __init__(self, func):
        self.func = func

    def __call__(self):
        pass
