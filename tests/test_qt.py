import sys; sys.path.insert(0, "./")
from oneface.core import *
from oneface.qt import *

import pytest


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


def test_int_with_default():
    @gui
    @one
    def func(a: Arg(int, [0, 10]) = 1):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == 1
    func.run_func()
    assert func.result == 1


def test_set_text():
    @gui
    @one
    def func(a: Arg(int, [0, 10], text="text a")):
        return a
    
    assert func.arg_widgets['a'].label.text() == "text a:"


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
    def func(a: Arg(str)):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == ""
    func.run_func()
    assert func.result == ""


def test_bool_input():
    @gui
    @one
    def func(a: Arg(bool), b: Arg(bool) = False):
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
    def func(a: Arg(Selection, ["a", "b"]) = "a"):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == "a"
    func.run_func()
    assert func.result == "a"


def test_subset_input():
    @gui
    @one
    def func(a: Arg(SubSet, ["a", "b"]) = ["a"]):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == ["a"]
    func.run_func()
    assert func.result == ["a"]


def test_inputpath_input():
    @gui
    @one
    def func(a: Arg(InputPath) = "a"):
        return a
    
    assert isinstance(func, GUI)
    kwargs = func.get_args()
    assert kwargs['a'] == "a"
    with pytest.raises(ArgsCheckError) as e:
        func.run_func()
    assert isinstance(e.value.args[0][0], ValueError)


if __name__ == "__main__":
    test_set_text()
