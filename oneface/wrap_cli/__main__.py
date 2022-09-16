import sys
import typing as T
import os.path as osp

import fire

from .wrap import WrapCLI
from ..core import one


FILE_DIR = osp.dirname(osp.abspath(__file__))
EXAMPLE_FILE = osp.join(FILE_DIR, "example.yaml")


def gen(target_path: str = "./example.yaml"):
    print(f"Generate an example config file in: {target_path}")
    with open(EXAMPLE_FILE) as f:
        content = f.read()
    with open(target_path, 'w') as f:
        f.write(content)


InterfaceTypes = T.Literal["cli", "qt_gui", "dash_app"]


def run(
        config_path: str, interface: InterfaceTypes,
        print_cmd: bool = True, **kwargs):
    """
    :param config_path: The path to your config(.yaml) file.
    :param interface: The interface type, 'qt_gui' | 'dash_app' | 'cli'
    :param print_cmd: Print the actually executed command or not.
    """
    wrap = WrapCLI.from_config_file(config_path, print_cmd=print_cmd)
    config = wrap.config
    of = one(wrap, **kwargs)
    if interface == "qt_gui":
        ret_code = of.qt_gui(**config.get('qt_config', {}))
    elif interface == "dash_app":
        ret_code = of.dash_app(**config.get('dash_config', {}))
    else:
        ret_code = of.cli()
    sys.exit(ret_code)


if __name__ == "__main__":
    fire.Fire({
        'run': run,
        'generate': gen,
    })
