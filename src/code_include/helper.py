#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extension-agnostic functions that other modules can freely use."""


def memoize(function):
    """Wrap a function with this decorator to cache its results.

    Reference:
        http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/#c1

    Args:
        function (callable):
            Some Python callable will become cache-able by this function.

    Returns:
        :class:`MemoDict`:
            A per-function instance gets called only once for a set of
            arguments once.

    """

    class MemoDict(dict):
        """A class that stores a function and caches each unique function call."""

        def __init__(self, function):
            super(MemoDict, self).__init__()

            self.function = function

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.function(*key)

            return ret

    return MemoDict(function)
