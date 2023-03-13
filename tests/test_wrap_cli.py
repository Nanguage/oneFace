import contextlib
from io import StringIO
import os.path as osp
import sys

from oneface.wrap_cli.wrap import wrap_cli, load_config


HERE = osp.dirname(osp.abspath(__file__))
example_yaml = osp.join(HERE, "../oneface/wrap_cli/example.yaml")


def test_load_config():
    conf = load_config(example_yaml)
    assert 'command' in conf
    assert 'inputs' in conf


def test_wrap_cli():
    conf = load_config(example_yaml)
    wrap = wrap_cli(conf)
    wrap(1, 2)
    assert wrap.__signature__ is not None


def test_retcode():
    conf = load_config(example_yaml)
    wrap = wrap_cli(conf)
    assert 0 == wrap(40, 2)


def test_stdout():
    conf = load_config(example_yaml)
    wrap = wrap_cli(conf, print_cmd=False)
    console_buffer = StringIO()
    wrap.out_stream = console_buffer
    wrap(40, 2)
    assert console_buffer.getvalue().strip() == "42"


def test_stderr():
    conf = load_config(example_yaml)
    wrap = wrap_cli(conf)
    console_buffer = StringIO()
    wrap.err_stream = console_buffer
    wrap(40, "aaa")
    assert "NameError" in console_buffer.getvalue()


def test_replace():
    conf = {
        "name": "test",
        "command": "python {c} 'print(1)'",
        "inputs": {
            "c": {
                "type": "bool",
                "true_insert": "-c",
                "default": True
            },
        },
    }
    wrap = wrap_cli(conf, print_cmd=True)
    assert 0 == wrap(True)


def test_stdout_block():
    conf = {
        "name": "test",
        "command": "python {v} -c 'print(1)'",
        "inputs": {
            "v": {
                "type": "bool",
                "true_insert": "-v",
                "default": True
            },
        },
    }
    wrap = wrap_cli(conf, print_cmd=True)
    console_buffer = StringIO()
    with contextlib.redirect_stderr(console_buffer):
        assert 0 == wrap(True)
