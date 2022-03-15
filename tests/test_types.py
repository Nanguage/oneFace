from oneface.types import *
from oneface.core import one, Arg, ArgsCheckError

import pytest


def test_selection():
    @one
    def func1(a: Arg(Selection, ["a", 2, 3])):
        print(a)
        return a

    assert func1("a") == "a"
    assert func1(2) == 2
    with pytest.raises(ArgsCheckError) as e:
        func1(1)
    assert isinstance(e.value.args[0][0], ValueError)


def test_subset():
    @one
    def func1(s: Arg(SubSet, [1,2,3])):
        print(s)
        return s

    assert func1([1, 2]) == [1, 2]
    with pytest.raises(ArgsCheckError) as e:
        func1([1, 2, 4])
    assert isinstance(e.value.args[0][0], ValueError)



def test_inputpath():
    @one
    def func1(s: Arg(InputPath)):
        print(s)
        return s

    assert func1(__file__) == __file__
    with pytest.raises(ArgsCheckError) as e:
        func1(1)
    assert isinstance(e.value.args[0][0], TypeError)
    with pytest.raises(ArgsCheckError) as e:
        func1("not/exists/file")
    assert isinstance(e.value.args[0][0], ValueError)


def test_outputpath():
    @one
    def func1(s: Arg(OutputPath)):
        print(s)
        return s

    assert func1(__file__) == __file__
    with pytest.raises(ArgsCheckError) as e:
        func1(1)
    assert isinstance(e.value.args[0][0], TypeError)
