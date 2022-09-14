import contextlib
from io import StringIO
import os.path as osp

from oneface.wrap_cli.wrap import WrapCLI, load_config, parse_arg_objs


HERE = osp.dirname(osp.abspath(__file__))
example_yaml = osp.join(HERE, "../oneface/wrap_cli/example.yaml")


def test_load_config():
    conf = load_config(example_yaml)
    assert 'command' in conf
    assert 'arguments' in conf


def test_parse_arg_objs():
    conf = load_config(example_yaml)
    arg_objs = parse_arg_objs(conf)
    assert len(arg_objs) > 0


def test_wrap_cli():
    conf = load_config(example_yaml)
    wrap = WrapCLI(conf)
    wrap(1, 2)
    assert wrap.__signature__ is not None


def test_retcode():
    wrap = WrapCLI.from_config_file(example_yaml)
    assert 0 == wrap(40, 2)


def test_stdout():
    wrap = WrapCLI.from_config_file(example_yaml, print_cmd=False)
    console_buffer = StringIO()
    with contextlib.redirect_stdout(console_buffer):
        wrap(40, 2)
    console_buffer.seek(0)
    content = console_buffer.read()
    assert content.strip() == "42"


def test_stderr():
    wrap = WrapCLI.from_config_file(example_yaml, print_cmd=False)
    console_buffer = StringIO()
    with contextlib.redirect_stderr(console_buffer):
        wrap(40, "aaa")
    console_buffer.seek(0)
    content = console_buffer.read()
    assert "NameError" in content


def test_replace():
    conf = {
        "name": "test",
        "command": "python {c} 'print(1)'",
        "arguments": {
            "c": {
                "type": "bool",
                "true_insert": "-c",
                "default": True
            },
        },
    }
    wrap = WrapCLI(conf, print_cmd=True)
    assert 0 == wrap(True)

