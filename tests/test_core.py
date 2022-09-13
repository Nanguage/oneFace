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
    @one(print_args=False)
    def func(a: Arg(int)):
        return a
    with pytest.raises(ArgsCheckError) as e:
        func(1.0)
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
        
        @one(print_args=False)
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
        


def test_parse_pass_in():
    def f1(a, b, c=1, d=2):
        pass
    arg_objs = get_func_argobjs(f1)
    vals = parse_pass_in((1, 2), {'d': 10}, arg_objs)
    assert (vals['a'] == 1) and (vals['b'] == 2) and (vals['c'] == 1) and (vals['d'] == 10)
    vals = parse_pass_in((1, 2, 3), {}, arg_objs)
    assert (vals['a'] == 1) and (vals['b'] == 2) and (vals['c'] == 3) and (vals['d'] == 2)
    with pytest.raises(ArgumentError):
        vals = parse_pass_in((1,), {}, arg_objs)
    vals = parse_pass_in([], {'a':1, 'b':2}, arg_objs)
    assert (vals['a'] == 1) and (vals['b'] == 2) and (vals['c'] == 1) and (vals['d'] == 2)


def test_docstring():
    @one
    def func1():
        "test"
        pass
    assert func1.__doc__ == "test"


def test_implicit():
    @one(print_args=False)
    def func(a: int):
        return a + 1
    assert func(1) == 2
    with pytest.raises(ArgsCheckError):
        func(1.0)
    @one(print_args=False)
    def func(a: Arg[int, [0, 10]], b: Arg[int, [0, 10]]):
        return a + b
    assert func(10, 10) == 20


if __name__ == "__main__":
    #test_arg_check()
    #test_arg_register()
    #test_print_args()
    #test_class_method_arg_check()
    test_implicit()
