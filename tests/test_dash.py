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

