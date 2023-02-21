import typing as T
import functools

from rich.console import Console
from rich.table import Table
from funcdesc.guard import Guard, TF2, CheckError
from funcdesc.desc import Description, Value

from .utils import get_callable_name


def check_args(func=None, **kwargs):
    if func is None:
        return functools.partial(check_args, **kwargs)
    return CallWithCheck(func, **kwargs)


console = Console()


class CallWithCheck(Guard[TF2]):
    def __init__(
            self,
            func: TF2,
            desc: T.Optional[Description] = None,
            check_inputs: bool = True,
            check_outputs: bool = False,
            check_side_effect: bool = False,
            check_type: bool = True,
            check_range: bool = True,
            print_args: bool = True,
            name: T.Optional[str] = None,
            ) -> None:
        self.name = get_callable_name(func, name)
        self.is_print_args = print_args
        self.table: T.Optional[Table] = None
        super().__init__(
            func, desc, check_inputs, check_outputs,
            check_side_effect, check_type, check_range,)

    def print_args(self):
        if self.table is None:
            return
        if self.name:
            console.print(f"Run: [bold purple]{self.name}")
        console.print("Arguments table:\n")
        console.print(self.table)
        console.print()

    def check_value(
            self,
            arg: Value,
            val: T.Any,
            errors: T.List[Exception]):
        val_str = str(val)
        range_str = str(arg.range)
        tp_str = str(type(val))
        ann_tp_str = str(arg.type)
        try:
            if self.is_check_type:
                arg.check_type(val)
            if self.is_check_range:
                arg.check_range(val)
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
            self.table.add_row(
                arg.name, ann_tp_str, range_str, val_str, tp_str)

    def check_inputs(self, pass_in: dict, errors: list):
        if self.is_print_args:
            self.table = self.get_argument_table()
        for val in self.desc.inputs:
            self.check_value(val, pass_in[val.name], errors)
        if self.is_print_args:
            self.print_args()
        if len(errors) > 0:
            raise CheckError(errors)

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
