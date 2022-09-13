from collections import OrderedDict
from ctypes import ArgumentError
import typing as T
import inspect
import re
import subprocess as subp

import yaml

from ..arg import Arg, Empty
from ..core import parse_pass_in


def load_config(path: str) -> dict:
    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


def parse_arg_objs(config: dict) -> T.OrderedDict[str, Arg]:
    args = OrderedDict()
    args_conf: dict = config['arguments']
    for n, p_conf in args_conf.items():
        p_conf: dict
        _tp = p_conf.get('type', 'str')
        _default = p_conf.get('default', Empty)
        _range = p_conf.get('range', None)
        arg = Arg(
            type=eval(_tp),
            range=_range,
            default=_default,
        )
        args[n] = arg
    return args


def compose_signature(args: T.OrderedDict[str, Arg]) -> inspect.Signature:
    parameters = []
    for name, arg_obj in args.items():
        param = inspect.Parameter(
            name, inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=arg_obj.default, annotation=arg_obj)
        parameters.append(param)
    sig = inspect.Signature(parameters)
    return sig


class Command(object):
    def __init__(self, template: str):
        self.template = template
        self.placeholders = [
            p.strip("{}") for p in
            re.findall(r"\{.*?\}", self.template)
        ]

    def check_placeholder(self, arg_names: T.List[str]):
        for arg in arg_names:
            if arg not in self.placeholders:
                raise ArgumentError(
                    f"The argument {arg} is not in command templates.")

    def format(self, vals: dict):
        for ph in self.placeholders:
            if ph not in vals:
                raise ValueError(
                    f"The value of placeholder {ph} is not provided.")
        cmd = self.template.format(**vals)
        return cmd


def run_process(exe):
    # https://stackoverflow.com/a/4760274/8500469
    p = subp.Popen(exe, stdout=subp.PIPE, stderr=subp.PIPE)
    while(True):
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break


class WrapCLI(object):
    def __init__(self, config: dict):
        self.config = config
        self.name = self.config['name']
        self.arg_objs = parse_arg_objs(config)
        self.command = Command(config['command'])
        self.command.check_placeholder(list(self.arg_objs.keys()))
        self.__signature__ = compose_signature(self.arg_objs)

    def __call__(self, *args, **kwargs):
        vals = parse_pass_in(args, kwargs, self.arg_objs)
        cmd_str = self.command.format(vals)
        for line in run_process(cmd_str):
            if line:
                print(line.decode().rstrip("\n"))

    @staticmethod
    def from_config_file(path: str) -> "WrapCLI":
        return WrapCLI(load_config(path))
