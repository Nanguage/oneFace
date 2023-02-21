import typing as T
import functools


class AllowWrapInstanceMethod(object):
    def __get__(self, obj, objtype):
        if not hasattr(self, "_bounded"):  # bound only once
            target_func = self.func
            bound_mth = functools.partial(target_func, obj)
            self.func = bound_mth
            self._bounded = True
        return self


def get_callable_name(func, name: T.Optional[str]) -> str:
    if name is not None:
        return name
    elif hasattr(func, "name"):
        return func.name
    else:
        return func.__name__
