import typing as T
import os.path as osp

import fire

from .wrap import WrapCLI
from ..core import one


FILE_DIR = osp.dirname(osp.abspath(__file__))
EXAMPLE_FILE = osp.join(FILE_DIR, "example.yaml")


def gen(target_path: str = "./oneface.yaml"):
    print(f"Generate an example config file in: {target_path}")
    with open(EXAMPLE_FILE) as f:
        content = f.read()
    with open(target_path, 'w') as f:
        f.write(content)


InterfaceTypes = T.Literal["cli", "qt", "dash"]


def run(config_path: str, interface: InterfaceTypes, **kwargs):
    wrap = WrapCLI.from_config_file(config_path)
    of = one(wrap, **kwargs)
    if interface == "qt":
        of.qt_gui()
    elif interface == "dash":
        of.dash_app()
    else:
        of.cli()


if __name__ == "__main__":
    fire.Fire({
        'run': run,
        'generate': gen,
    })
