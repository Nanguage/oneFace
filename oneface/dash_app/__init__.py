import functools

from .app import App
from .embed import flask_route


def app(func=None, **kwargs):
    if func is None:
        return functools.partial(app, **kwargs)
    return App(func, **kwargs)


__all__ = ["app", "App", "flask_route"]
