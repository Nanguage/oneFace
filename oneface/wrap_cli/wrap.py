import sys
import shlex
import typing as T
import inspect
import re
import subprocess as subp
from collections import OrderedDict
from ctypes import ArgumentError
from threading import Thread
from queue import Queue

import yaml

from ..arg import Arg, Empty
from ..core import parse_pass_in


def load_config(path: str) -> dict:
    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


def extrace_key(d: dict, key, default) -> T.Any:
    if key in d:
        return d.pop(key)
    else:
        return default


def parse_arg_objs(config: dict) -> T.OrderedDict[str, Arg]:
    args = OrderedDict()
    args_conf: dict = config['arguments']
    for n, p_conf in args_conf.items():
        p_conf: dict = p_conf.copy()
        _tp = extrace_key(p_conf, 'type', 'str')
        _default = extrace_key(p_conf, 'default', Empty)
        _range = extrace_key(p_conf, 'range', None)
        arg = Arg(
            type=eval(_tp),
            range=_range,
            default=_default,
            **p_conf
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


def replace_vals(vals: dict, arg_objs: T.OrderedDict[str, Arg]) -> dict:
    vals = vals.copy()
    for key, val in vals.items():
        arg_obj = arg_objs[key]
        if (val is True) and ('true_insert' in arg_obj.kwargs):
            vals[key] = arg_obj.kwargs['true_insert']
        if (val is False) and ('false_insert' in arg_obj.kwargs):
            vals[key] = arg_obj.kwargs['false_insert']
    return vals


def run_process(exe):
    # https://stackoverflow.com/a/4760274/8500469
    p = subp.Popen(exe, stdout=subp.PIPE, stderr=subp.PIPE)
    while True:
        # returns None while subprocess is running
        retcode = p.poll()
        out_line = p.stdout.readline()
        if out_line:
            yield 'stdout', out_line.decode()
        err_line = p.stderr.readline()
        if err_line:
            yield 'stderr', err_line.decode()
        if retcode is not None:
            break
    return retcode


class ProcessRunner(object):
    """Subprocess runner, allow stream stdout and stderr."""
    def __init__(self, command: str) -> None:
        self.command = command
        self.queue = Queue()
        self.proc = None
        self.t_stdout = None
        self.t_stderr = None

    def run(self):
        exe = shlex.split(self.command)
        self.proc = subp.Popen(exe, stdout=subp.PIPE, stderr=subp.PIPE)
        self.proc.stdout
        self.t_stdout = Thread(
            target=self.reader_func, args=(self.proc.stdout, self.queue))
        self.t_stdout.start()
        self.t_stderr = Thread(
            target=self.reader_func, args=(self.proc.stderr, self.queue))
        self.t_stderr.start()

    @staticmethod
    def reader_func(pipe: T.IO[bytes], queue: "Queue"):
        """https://stackoverflow.com/a/31867499/8500469"""
        try:
            with pipe:
                for line in iter(pipe.readline, b''):
                    queue.put((pipe, line))
        finally:
            queue.put(None)

    def stream(self):
        """https://stackoverflow.com/a/31867499/8500469"""
        for _ in range(2):
            for source, line in iter(self.queue.get, None):
                if source is self.proc.stdout:
                    src = "stdout"
                else:
                    src = "stderr"
                yield src, line.decode()
        return self.proc.wait()


class WrapCLI(object):
    def __init__(self, config: dict, print_cmd=True):
        self.config = config
        self.name = self.config['name']
        self.arg_objs = parse_arg_objs(config)
        self.command = Command(config['command'])
        self.command.check_placeholder(list(self.arg_objs.keys()))
        self.__signature__ = compose_signature(self.arg_objs)
        self.is_print_cmd = print_cmd

    def __call__(self, *args, **kwargs) -> int:
        vals = parse_pass_in(args, kwargs, self.arg_objs)
        vals = replace_vals(vals, self.arg_objs)
        cmd_str = self.command.format(vals)
        if self.is_print_cmd:
            print(f"Run command: {cmd_str}")
        runner = ProcessRunner(cmd_str)
        runner.run()
        g = runner.stream()
        retcode = None
        while True:
            try:
                src, line = next(g)
                if src == 'stdout':
                    print(line.rstrip("\n"))
                else:
                    print(line.rsplit("\n"), file=sys.stderr)
            except StopIteration as e:
                retcode = e.value
                break
        return retcode

    @staticmethod
    def from_config_file(path: str, *args, **kwargs) -> "WrapCLI":
        return WrapCLI(load_config(path), *args, **kwargs)
