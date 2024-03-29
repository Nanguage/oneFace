from oneface.core import *
from oneface.check import *
from oneface.qt import *
from funcdesc import Val

import pytest


def test_int_input():
    @gui
    @one
    def func(a: Val(int, [0, 10])):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 0
    func.run_func()
    assert func.result == 0


def test_int_with_default():
    @gui
    @one
    def func(a: Val(int, [0, 10]) = 1):
        return a

    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 1
    func.run_func()
    assert func.result == 1


def test_set_text():
    @gui
    @one
    def func(a: Val(int, [0, 10], text="text a")):
        return a
    
    assert func.arg_widgets['a'].label.text() == "text a:"


def test_float_input():
    @gui
    @one
    def func(a: Val(float, [0, 10])):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 0.0
    func.run_func()
    assert func.result == 0.0


def test_str_input():
    @gui
    @one
    def func(a: Val(str)):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == ""
    func.run_func()
    assert func.result == ""


def test_bool_input():
    @gui
    @one
    def func(a: Val(bool), b: Val(bool) = False):
        return a, b
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == True
    assert kwargs['b'] == False
    func.run_func()
    assert func.result == (True, False)


def test_selection_input():
    @gui
    @one
    def func(a: Val(OneOf, ["a", "b"]) = "a"):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == "a"
    func.run_func()
    assert func.result == "a"


def test_subset_input():
    @gui
    @one
    def func(a: Val(SubSet, ["a", "b"]) = ["a"]):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == ["a"]
    func.run_func()
    assert func.result == ["a"]


def test_inputpath_input():
    @gui
    @one
    def func(a: Val(InputPath) = "a"):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == "a"
    with pytest.raises(CheckError) as e:
        func.run_func()
    assert isinstance(e.value.args[0][0], ValueError)


def test_on_native_func():
    @gui
    def func(a: int, b: float):
        return a + b

    assert isinstance(func, GUI)

    class A():
        @gui
        def mth1(self, name: str, weight: float):
            return name, weight

    a = A()
    assert isinstance(a.mth1, GUI)


if __name__ == "__main__":
    test_set_text()
