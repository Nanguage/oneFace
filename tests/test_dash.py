from oneface.dash_app import *
from oneface.core import one, Arg


def test_app_create():
    @app
    @one
    def func(a: Arg(int, [0, 10]), b: Arg(float, [0, 5])):
        return a + b
    
    assert func.dash_app is not None
    assert func.input_names == ['a', 'b']
    assert func.input_types == [int, float]


def test_field_default_value():
    @app
    @one
    def func(a: Arg[int, [-10, 10]] = 0,
             b: int = 20):
        return a + b

    assert 0 == func.dash_app.layout.children[1].children[1].value
    assert 20 == func.dash_app.layout.children[2].children[1].value


    @app
    @one
    def func1(a: bool):
        return a

    assert 'True' == func1.dash_app.layout.children[1].children[1].value

