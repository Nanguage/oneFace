from one.core import *

def test_arg_check():

    @one
    def func(a: Arg(int, [0, 10])):
        pass

    func()
