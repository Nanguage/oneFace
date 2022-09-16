from oneface.dash_app import *
from oneface.core import one, Arg


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


def test_download_type():
    @app(result_type="download")
    @one
    def func(a: str):
        return ""

    assert func.get_dash_app is not None
