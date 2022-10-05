import functools


class AllowWrapInstanceMethod(object):
    def __get__(self, obj, objtype):
        if not hasattr(self, "_bounded"):  # bound only once
            target_func = self.func
            bound_mth = functools.partial(target_func, obj)
            self.func = bound_mth
            self._bounded = True
        return self
