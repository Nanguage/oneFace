import yaml
from cmd2func import cmd2func
from cmd2func.config import CLIConfig
from funcdesc import mark_input


def load_config(path: str) -> dict:
    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


def wrap_cli(config: CLIConfig, print_cmd=True):
    func = cmd2func(config['command'], config, print_cmd=print_cmd)
    for name, arg in config['inputs'].items():
        if 'range' in arg:
            func = mark_input(name, range=arg['range'])(func)
    func.name = config['name']
    return func
