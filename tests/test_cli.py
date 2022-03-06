import sys
sys.path.insert(0, "./")
from oneface.core import *

def run_cli():
    @one
    def func(a: Arg(int, [0, 10])):
        print(a)

    func.cli()
    

if __name__ == "__main__":
    run_cli()
