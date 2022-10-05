from oneface.dash_app import *
from oneface.core import one
from oneface.arg import Arg
from oneface.dash_app.embed import flask_route

from dash import dcc


def test_app_create():
    @app
    @one
    def func(a: Arg(int, [0, 10]), b: Arg(float, [0, 5])):
        return a + b
    
    assert func.get_dash_app() is not None
    assert func.input_names == ['a', 'b']
    assert func.input_types == [int, float]


def test_field_default_value():
    @app
    @one
    def func(a: Arg[int, [-10, 10]] = 0,
             b: int = 20):
        return a + b

    dash_app = func.get_dash_app()
    assert 0 == dash_app.layout.children[1].children[1].value
    assert 20 == dash_app.layout.children[2].children[1].value

    @app
    @one
    def func1(a: bool):
        return a

    dash_app = func1.get_dash_app()
    assert 'True' == dash_app.layout.children[1].children[1].value


def test_download_show_type():
    @app(result_show_type="download")
    @one
    def func(a: str):
        return ""

    dash_app = func.get_dash_app()
    assert isinstance(dash_app.layout.children[-1], dcc.Download)


def test_plotly_show_type():
    @app(result_show_type="plotly")
    @one
    def func():
        import plotly.express as px
        fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
        return fig

    dash_app = func.get_dash_app()
    assert isinstance(dash_app.layout.children[-1], dcc.Graph)


def test_embed():
    from flask import Flask

    server = Flask("test")

    @flask_route(server, "/dash")
    @app
    @one
    def func(name: str):
        return name
    

def test_on_native_func():
    @app
    def func(a: int, b: float):
        return a + b

    assert func.get_dash_app() is not None
    assert func.input_names == ['a', 'b']
    assert func.input_types == [int, float]

    class A():
        @app
        def mth1(self, name: str, weight: float):
            return name, weight
    
    a = A()
    assert a.mth1.get_dash_app() is not None
    assert a.mth1.input_names == ['name', 'weight']
    assert a.mth1.input_types == [str, float]
