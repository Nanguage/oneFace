import inspect
import sys
sys.path.insert(0, "./")
from oneface.core import *

import pytest


def test_arg_check():
    @one(print_args=False)
    def func(a: Arg(int, [0, 10]), b: Arg(float, [0, 1]), k=10):
        return a
    assert func(10, 0.3) == 10
    with pytest.raises(ArgsCheckError) as e:
        func(11, 0.3)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(ArgsCheckError) as e:
        func(2.0, 0.3)
    assert isinstance(e.value.args[0][0], TypeError)
    with pytest.raises(ArgsCheckError) as e:
        func("str", 0.3)
    assert isinstance(e.value.args[0][0], TypeError)
    with pytest.raises(ArgsCheckError) as e:
        func(2, 10.0)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(ArgsCheckError) as e:
        func(-1, 1)
    assert isinstance(e.value.args[0][0], ValueError)
    assert isinstance(e.value.args[0][1], TypeError)
    func(2, 0.5)
    @one(print_args=False)
    def func(a: Arg(bool)):
        pass
    with pytest.raises(ArgsCheckError) as e:
        func(1)
    assert isinstance(e.value.args[0][0], TypeError)


def test_arg_register():
    @one(print_args=False)
    def func(a: Arg(list, None)):
        pass
    with pytest.raises(NotImplementedError):
        func([0,1])
    Arg.register_type_check(list)
    func([1,2,3])
    with pytest.raises(ArgsCheckError) as e:
        func(True)
    assert isinstance(e.value.args[0][0], TypeError)


def test_print_args():
    @one
    def func(a: Arg(int, [0, 10]), b: Arg(float, [0, 1])):
        return a + b
    func(3, 0.5)
    with pytest.raises(ArgsCheckError) as e:
        func(-1, 1.0)
    with pytest.raises(ArgsCheckError) as e:
        func(0.1, 1)


def test_class_method_arg_check():
    class A():
        def __init__(self, a):
            self.a = a
        
        @one
        def mth1(self, b: Arg(float, [0, 1])):
            return self.a + b

    a = A(10)
    assert a.mth1(0.1) == 10.1
    with pytest.raises(ArgsCheckError) as e:
        a.mth1(10.0)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(ArgsCheckError) as e:
        a.mth1(False)
    assert isinstance(e.value.args[0][0], TypeError)
        


def test_parse_args_kwargs():
    def f1(a, b, c=1, d=2):
        pass
    sig = inspect.signature(f1)
    args = parse_args_kwargs((1, 2), {'d': 10}, sig)
    assert (args['a'] == 1) and (args['b'] == 2) and (args['c'] == 1) and (args['d'] == 10)
    args = parse_args_kwargs((1, 2, 3), {}, sig)
    assert (args['a'] == 1) and (args['b'] == 2) and (args['c'] == 3) and (args['d'] == 2)
    with pytest.raises(ArgumentError):
        args = parse_args_kwargs((1,), {}, sig)
    args = parse_args_kwargs([], {'a':1, 'b':2}, sig)
    assert (args['a'] == 1) and (args['b'] == 2) and (args['c'] == 1) and (args['d'] == 2)


if __name__ == "__main__":
    #test_arg_check()
    #test_arg_register()
    #test_print_args()
    test_class_method_arg_check()
