from pathlib import Path

from oneface.core import Arg


class ArgType(object):
    @staticmethod
    def check_type(val, type_):
        return True

    @staticmethod
    def check_range(val, range_):
        return True


class Selection(ArgType):
    @staticmethod
    def check_range(val, range_):
        return val in range_


class SubSet(ArgType):
    @staticmethod
    def check_range(val, range_):
        return all([v in range_ for v in val])


class InputPath(ArgType):
    @staticmethod
    def check_type(val, type_):
        return isinstance(val, str) or isinstance(val, Path)

    @staticmethod
    def check_range(val, range_):
        path = Path(val) if isinstance(val, str) else val
        return path.exists()


class OutputPath(ArgType):
    @staticmethod
    def check_type(val, type_):
        return isinstance(val, str) or isinstance(val, Path)


Arg.register_range_check(Selection, Selection.check_range)
Arg.register_range_check(SubSet, SubSet.check_range)
Arg.register_type_check(InputPath, InputPath.check_type)
Arg.register_range_check(InputPath, InputPath.check_range)
Arg.register_type_check(OutputPath, OutputPath.check_type)
