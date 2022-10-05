import functools

from .check import CallWithCheck


def one(func=None, **kwargs):
    if func is None:
        return functools.partial(one, **kwargs)
    return One(func, **kwargs)


class One(CallWithCheck):

    def cli(self):
        from fire import Fire
        Fire(self.__call__)

    def qt_gui(self, **kwargs):
        from .qt import GUI
        return GUI(self, **kwargs)()

    def dash_app(self, **kwargs):
        from .dash_app import App
        return App(self, **kwargs)()
