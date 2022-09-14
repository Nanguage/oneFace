import typing as T
import inspect
from collections import OrderedDict


class Empty:
    pass


class ArgMeta(type):
    def __getitem__(self, args):
        if isinstance(args, tuple):
            return Arg(*args)
        else:
            return Arg(args)


class Arg(metaclass=ArgMeta):
    type_to_range_checker = {}
    type_to_type_checker = {}

    def __init__(self, type: type = str, range=None, default=Empty, **kwargs):
        self.type = type
        self.range = range
        self.default = default
        self.kwargs = kwargs

    @property
    def type_checker(self):
        return self.type_to_type_checker.get(self.type.__name__, None)

    @property
    def range_checker(self):
        return self.type_to_range_checker.get(self.type.__name__, None)

    def check(self, val):
        if (self.range_checker is None) and (self.type_checker is None):
            raise NotImplementedError(
                f"Not checker registered for type: {type}")
        if self.type_checker is not None:
            if not self.type_checker(val, self.type):
                raise TypeError(
                    f"Input value {val} is not in valid type({self.type})")
        if (self.range_checker is not None):
            if (not self.range_checker(val, self.range)):
                raise ValueError(f"Input value {val} is not in a valid range.")

    @classmethod
    def register_range_check(cls, type, checker):
        cls.type_to_range_checker[type.__name__] = checker

    @classmethod
    def register_type_check(cls, type, checker=None):
        checker = checker or (lambda v, t: isinstance(v, t))
        cls.type_to_type_checker[type.__name__] = checker


# register basic types
def _check_number_in_range(v, range):
    return (range is None) or (range[0] <= v <= range[1])


Arg.register_type_check(Empty, lambda v, range: True)
Arg.register_type_check(str)
Arg.register_range_check(int, _check_number_in_range)
Arg.register_type_check(int)
Arg.register_range_check(float, _check_number_in_range)
Arg.register_type_check(float)
Arg.register_type_check(bool)


def get_func_argobjs(func: T.Callable) -> T.OrderedDict[str, Arg]:
    args = OrderedDict()
    sig = inspect.signature(func)
    for n, p in sig.parameters.items():
        ann = p.annotation
        if isinstance(ann, Arg):
            arg = ann
        elif isinstance(ann, tuple):
            arg = Arg(*ann)
        elif ann is inspect._empty:
            arg = Arg(Empty)
        else:
            arg = Arg(ann)
        if p.default is not inspect._empty:
            arg.default = p.default
        args[n] = arg
    return args
