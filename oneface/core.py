from copy import copy
from ctypes import ArgumentError
import inspect
import functools

from rich.console import Console
from rich.table import Table


console = Console()


class Arg():

    type_to_range_checker = {}
    type_to_type_checker = {}

    def __init__(self, type=str, range=None, **kwargs):
        self.type = type
        self.range = range
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
        if self.range_checker is not None:
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
Arg.register_type_check(str)
Arg.register_range_check(int, lambda v, range: range[0] <= v <= range[1])
Arg.register_type_check(int)
Arg.register_range_check(float, lambda v, range: range[0] <= v <= range[1])
Arg.register_type_check(float)
Arg.register_type_check(bool)


def parse_args_kwargs(args: tuple, kwargs: dict, func: object):
    """Get the pass in value of the func
    arguments according to it's signature."""
    args = list(args)
    kwargs = copy(kwargs)
    res = {}
    sig = inspect.signature(func)
    for n, p in sig.parameters.items():
        has_default = p.default is not inspect._empty
        if len(args) > 0:
            res[n] = args.pop(0)
        elif (len(kwargs) > 0) and (n in kwargs):
            res[n] = kwargs.pop(n)
        else:
            if has_default:
                res[n] = p.default
            else:
                raise ArgumentError(
                    f"{n} is not provided and has no default value.")
    return res


class ArgsCheckError(Exception):
    pass


def one(func=None, **kwargs):
    if func is None:
        return functools.partial(one, **kwargs)
    return One(func, **kwargs)


class One(object):
    def __init__(self, func, print_args=True, name=None):
        self.func = func
        functools.update_wrapper(self, func)
        self.name = name if name is not None else func.__name__
        self.print_args = print_args
        self.table = None

    def __call__(self, *args, **kwargs):
        self.table = self.get_argument_table()
        sig = inspect.signature(self.func)
        # check args
        vals = parse_args_kwargs(args, kwargs, self.func)
        errors = []
        for n, p in sig.parameters.items():
            self._check_arg(n, p.annotation, vals[n], errors)
        if self.print_args:
            if self.name:
                console.print(f"Run: [bold purple]{self.name}")
            console.print("Arguments table:\n")
            console.print(self.table)
            console.print()
        if len(errors) > 0:
            raise ArgsCheckError(errors)
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype):
        """Support instance method
        see https://stackoverflow.com/a/3296318/8500469"""
        return functools.partial(self.__call__, obj)

    def _check_arg(self, name, ann, val, errors):
        if not isinstance(ann, Arg):
            return
        val_str = str(val)
        range_str = str(ann.range)
        tp_str = str(type(val))
        ann_tp_str = str(ann.type)
        try:
            ann.check(val)
        except Exception as e:
            errors.append(e)
            if isinstance(e, ValueError):
                val_str = f"[red]{val_str}[/red]"
                range_str = f"[red]{range_str}[/red]"
            elif isinstance(e, TypeError):
                ann_tp_str = f"[red]{ann_tp_str}[/red]"
                tp_str = f"[red]{tp_str}[/red]"
            else:
                raise e
        self.table.add_row(name, ann_tp_str, range_str, val_str, tp_str)

    @staticmethod
    def get_argument_table():
        table = Table(
            show_header=True, header_style="bold magenta",
            box=None)
        table.add_column("Argument")
        table.add_column("Type")
        table.add_column("Range")
        table.add_column("InputVal")
        table.add_column("InputType")
        return table

    def cli(self):
        from fire import Fire
        Fire(self.__call__)

    def qt_gui(self, **kwargs):
        from .qt import GUI
        return GUI(self, **kwargs)()

    def dash_app(self, **kwargs):
        from .dash_app import App
        return App(self, **kwargs)()
