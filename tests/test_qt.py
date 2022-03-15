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
