from copy import copy
from ctypes import ArgumentError
import inspect
import functools

from rich.console import Console
from rich.table import Table


console = Console()


class Arg():

    type_to_range_checker = {}
    check_type = set()

    def __init__(self, type=str, range=None, **kwargs):
        self.type = type
        self.range = range
        self.kwargs = kwargs

    @property
    def is_check_type(self):
        return self.type.__name__ in self.check_type

    @property
    def range_checker(self):
        return self.type_to_range_checker.get(self.type.__name__, None)

    def check(self, val):
        if (self.range_checker is None) and (not self.is_check_type):
            raise NotImplementedError(
                f"Not checker registered for type: {type}")
        if self.is_check_type and (type(val) is not self.type):
            raise TypeError(
                f"Input value {val} is not in valid type({self.type})")
        if (self.range is not None) and (self.range_checker is not None):
            if (not self.range_checker(val, self.range)):
                raise ValueError(f"Input value {val} is not in a valid range.")

    @classmethod
    def register_range_check(cls, type, range_check_func):
        cls.type_to_range_checker[type.__name__] = range_check_func

    @classmethod
    def register_type_check(cls, type):
        cls.check_type.add(type.__name__)


# register basic types
Arg.register_range_check(str, lambda v, range: v in range)
Arg.register_type_check(str)
Arg.register_range_check(int, lambda v, range: range[0] <= v <= range[1])
Arg.register_type_check(int)
Arg.register_range_check(float, lambda v, range: range[0] <= v <= range[1])
Arg.register_type_check(float)
Arg.register_type_check(bool)


def parse_args_kwargs(args: tuple, kwargs: dict, signature: inspect.Signature):
    """Get the pass in value of the func
    arguments according to it's signature."""
    args = list(args)
    kwargs = copy(kwargs)
    res = {}
    for n, p in signature.parameters.items():
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


def argument_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Argument")
    table.add_column("Type")
    table.add_column("Range")
    table.add_column("InputVal")
    table.add_column("InputType")
    return table


class ArgsCheckError(Exception):
    pass


def one(func=None, *, print_args=True, name=None):
    if func is None:
        return functools.partial(one, print_args=print_args)
    sig = inspect.signature(func)

    @functools.wraps(func)
    def func_(*args, **kwargs):
        table = argument_table()
        # check args
        vals = parse_args_kwargs(args, kwargs, sig)
        errors = []
        for n, p in sig.parameters.items():
            ann = p.annotation
            if isinstance(ann, Arg):
                val = vals[n]
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
                table.add_row(n, ann_tp_str, range_str, val_str, tp_str)

        name_print = name if name is not None else func.__name__
        if name_print:
            console.rule(f"Run: [bold purple]{name_print}")
        if print_args:
            console.print("Arguments table:")
            console.print(table)
            console.print()
        if len(errors) > 0:
            raise ArgsCheckError(errors)
        return func(*args, **kwargs)

    import fire
    func_.cli = lambda: fire.Fire(func_)

    return func_
