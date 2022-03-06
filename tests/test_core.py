import inspect
import sys
sys.path.insert(0, "./")
from oneface.core import *

import pytest


def test_arg_check():
    @one
    def func(a: Arg(int, [0, 10]), b: Arg(float, [0, 1]), k=10):
        return a
    assert func(10, 0.3) == 10
    with pytest.raises(ValueError):
        func(11, 0.3)
    with pytest.raises(ValueError):
        func(2.0, 0.3)
    with pytest.raises(ValueError):
        func("str", 0.3)
    with pytest.raises(ValueError):
        func(2, 10.0)
    func(2, 0.5)
    @one
    def func(a: Arg(bool)):
        pass
    with pytest.raises(ValueError):
        func(1)


def test_arg_register():
    @one
    def func(a: Arg(list, None)):
        pass
    with pytest.raises(NotImplementedError):
        func([0,1])
    Arg.register_type_check(list)
    func([1,2,3])
    with pytest.raises(ValueError):
        func(True)


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
    test_arg_register()
