import typing as T

from flask import Flask
from dash import Dash

from .app import App


class RouteFunc():
    def __init__(self, dash_app: "Dash", name: str):
        self.dash_app = dash_app
        self.__name__ = name

    def __call__(self):
        return self.dash_app.index()


def flask_route(
        server: "Flask", rule: str,
        dash_app_kwargs: T.Optional[dict] = None,
        **options):
    def deco(func: T.Callable):
        if isinstance(func, App):
            dash_wrap = func
        else:
            dash_wrap = App(func)
        base_path = rule if rule.endswith('/') else (rule + "/")
        if dash_app_kwargs is None:
            d_kwargs = {}
        else:
            d_kwargs = dash_app_kwargs
        dash_app = dash_wrap.get_dash_app(
            server=server, url_base_pathname=base_path,
            **d_kwargs,
        )
        dash_app_route = RouteFunc(dash_app, dash_wrap.name)
        server.route(rule, **options)(dash_app_route)
        return func
    return deco
