from oneface.core import *
from oneface.check import *
from funcdesc import Val
from funcdesc.guard import CheckError

import pytest


def test_arg_check():
    @check_args(print_args=False)
    def func(a: Val(int, [0, 10]), b: Val(float, [0, 1]), k=10):
        return a
    assert func(10, 0.3) == 10
    with pytest.raises(CheckError) as e:
        func(11, 0.3)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(CheckError) as e:
        func(2.0, 0.3)
    assert isinstance(e.value.args[0][0], TypeError)
    with pytest.raises(CheckError) as e:
        func("str", 0.3)
    assert isinstance(e.value.args[0][0], TypeError)
    with pytest.raises(CheckError) as e:
        func(2, 10.0)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(CheckError) as e:
        func(-1, 1)
    assert isinstance(e.value.args[0][0], ValueError)
    assert isinstance(e.value.args[0][1], TypeError)
    func(2, 0.5)
    @check_args(print_args=False)
    def func(a: Val(bool)):
        pass
    with pytest.raises(CheckError) as e:
        func(1)
    @check_args(print_args=False)
    def func(a: Val(int)):
        return a
    with pytest.raises(CheckError) as e:
        func(1.0)
    assert isinstance(e.value.args[0][0], TypeError)


def test_arg_register():
    @check_args(print_args=False)
    def func(a: Val(list, None)):
        pass
    Val.register_type_check(list)
    func([1,2,3])
    with pytest.raises(CheckError) as e:
        func(True)
    assert isinstance(e.value.args[0][0], TypeError)


def test_print_args():
    @check_args(print_args=True)
    def func(a: Val(int, [0, 10]), b: Val(float, [0, 1])):
        return a + b
    func(3, 0.5)
    with pytest.raises(CheckError) as e:
        func(-1, 1.0)
    with pytest.raises(CheckError) as e:
        func(0.1, 1)


def test_class_method_arg_check():
    class A():
        def __init__(self, a):
            self.a = a
        
        @check_args(print_args=False)
        def mth1(self, b: Val(float, [0, 1])):
            return self.a + b

    a = A(10)
    assert a.mth1(0.1) == 10.1
    with pytest.raises(CheckError) as e:
        a.mth1(10.0)
    assert isinstance(e.value.args[0][0], ValueError)
    with pytest.raises(CheckError) as e:
        a.mth1(False)
    assert isinstance(e.value.args[0][0], TypeError)
        

def test_docstring():
    @check_args
    def func1():
        "test"
        pass
    assert func1.__doc__ == "test"


def test_implicit():
    @one(print_args=False)
    def func(a: int):
        return a + 1
    assert func(1) == 2
    with pytest.raises(CheckError):
        func(1.0)
    @one(print_args=False)
    def func(a: Val[int, [0, 10]], b: Val[int, [0, 10]]):
        return a + b
    assert func(10, 10) == 20


if __name__ == "__main__":
    #test_arg_check()
    #test_arg_register()
    #test_print_args()
    #test_class_method_arg_check()
    test_implicit()
