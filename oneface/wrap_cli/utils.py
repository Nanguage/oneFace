import typing as T
import yaml


def load_config(path: str) -> dict:
    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


def config_to_subprocess_call(config: dict) -> T.Callable:
    pass
