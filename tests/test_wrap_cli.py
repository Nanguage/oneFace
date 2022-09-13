import os.path as osp

from yaml import load

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

