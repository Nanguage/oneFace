import sys
sys.path.insert(0, "./")
import subprocess
from oneface.core import *
import pytest


@one
def cli_func(a: Arg(int, [0, 10])):
    print(a)


current_file = "tests/test_cli.py"


def test_cli():
    p = subprocess.Popen(f"python {current_file} 10", shell=True, stdout=subprocess.PIPE)
    outs, errs = p.communicate()
    assert "\n10" in outs.decode("utf8")
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(f"python {current_file} 100", shell=True)


if __name__ == "__main__":
    cli_func.cli()
