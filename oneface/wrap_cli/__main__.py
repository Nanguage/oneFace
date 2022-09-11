import os.path as osp

import fire


FILE_DIR = osp.dirname(osp.abspath(__file__))
EXAMPLE_FILE = osp.join(FILE_DIR, "example.yaml")


def gen(target_path: str = "./oneface.yaml"):
    print(f"Generate an example config file in: {target_path}")
    with open(EXAMPLE_FILE) as f:
        content = f.read()
    with open(target_path, 'w') as f:
        f.write(content)


def run():
    pass


if __name__ == "__main__":
    fire.Fire({
        'run': run,
        'generate': gen,
    })
