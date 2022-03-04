import inspect
import functools


class Arg():

    type_to_check = {}

    def __init__(self, type=str, range=None, **kwargs):
        self.type = type
        try:
            self.check_type, self.check_func = self.type_to_check[type.__name__]
        except KeyError:
            raise NotImplemented(f"Not check function for type: {type}")
        self.range = range
        self.kwargs = kwargs

    def check(self, val):
        if self.check_type and (type(val) is not self.type):
            raise ValueError(f"Input value {val} is not in valid type({self.type})")
        if self.range is None:
            return
        if (self.check_func is not None) and (not self.check_func(val)):
            raise ValueError(f"Input value {val} is not in a valid range.")

    @classmethod
    def register_type_check(cls, type, check_func=None, check_type=False):
        cls.type_to_check[type.__name__] = (check_func, check_type)


Arg.register_type_check(str, lambda v, range: v in range, True)
Arg.register_type_check(int, lambda v, range: range[0] <= v <= range[1], True)
Arg.register_type_check(float, lambda v, range: range[0] <= v <= range[1], True)
Arg.register_type_check(bool, None, True)


def one(func):
    sig = inspect.signature(func)
    @functools.wraps(func)
    def func_(*args, **kwargs):
        func(*args, **kwargs)
    return func_
