import typing as T
from copy import copy
from ctypes import ArgumentError
import functools

from rich.console import Console
from rich.table import Table

from .arg import Empty, Arg, parse_func_args
from .utils import AllowWrapInstanceMethod


def check_args(func=None, **kwargs):
    if func is None:
        return functools.partial(check_args, **kwargs)
    return CallWithCheck(func, **kwargs)


console = Console()


class ArgsCheckError(Exception):
    pass


def parse_pass_in(
        args: tuple, kwargs: dict,
        arg_objs: T.OrderedDict[str, "Arg"]):
    """Get the pass in value of the func
    arguments according to it's signature."""
    args_ = list(args)
    kwargs = copy(kwargs)
    res = {}
    for n, a in arg_objs.items():
        has_default = a.default is not Empty
        if len(args_) > 0:
            res[n] = args_.pop(0)
        elif (len(kwargs) > 0) and (n in kwargs):
            res[n] = kwargs.pop(n)
        else:
            if has_default:
                res[n] = a.default
            else:
                raise ArgumentError(
                    f"{n} is not provided and has no default value.")
    return res


class CallWithCheck(AllowWrapInstanceMethod):
    def __init__(self, func, print_args=True, name=None):
        self.func = func
        functools.update_wrapper(self, func)
        if name is not None:
            self.name = name
        elif hasattr(func, "name"):
            self.name = func.name
        else:
            self.name = func.__name__
        self.is_print_args = print_args
        self.table = None

    def __call__(self, *args, **kwargs):
        arg_objs = parse_func_args(self.func)
        if self.is_print_args:
            self.table = self.get_argument_table()
        # check args
        vals = parse_pass_in(args, kwargs, arg_objs)
        errors = []
        for n, arg in arg_objs.items():
            self._check_arg(n, arg, vals[n], errors)
        if self.is_print_args:
            self.print_args()
        if len(errors) > 0:
            raise ArgsCheckError(errors)
        return self.func(*args, **kwargs)

    def print_args(self):
        if self.name:
            console.print(f"Run: [bold purple]{self.name}")
        console.print("Arguments table:\n")
        console.print(self.table)
        console.print()

    def _check_arg(
            self, name: str, arg: Arg,
            val: T.Any, errors: T.List[Exception]):
        val_str = str(val)
        range_str = str(arg.range)
        tp_str = str(type(val))
        ann_tp_str = str(arg.type)
        try:
            arg.check(val)
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
        if self.is_print_args:
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
