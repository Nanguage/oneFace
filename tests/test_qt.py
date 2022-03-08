from oneface.core import *
from oneface.qt import *


def test_int_input():
    @gui
    @one
    def func(a: Arg(int, [0, 10])):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 0
    func.run_func()
    assert func.result == 0


def test_float_input():
    @gui
    @one
    def func(a: Arg(float, [0, 10])):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 0.0
    func.run_func()
    assert func.result == 0.0


def test_str_input():
    @gui
    @one
    def func(a: Arg(str, ["a", "b"])):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == "a"
    func.run_func()
    assert func.result == "a"
