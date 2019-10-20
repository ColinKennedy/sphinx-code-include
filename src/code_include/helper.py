#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extension-agnostic functions that other modules can freely use."""


def memoize(function):
    """Wrap a function with this decorator to cache its results.

    Reference:
        http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/#c1

    Args:
        function (callable):
            Some Python callable that will be memoized by this function.

    Returns:
        :class:`memodict`:
            A per-function instance that will only ever be called for a
            set of arguments once.

    """
    class memodict(dict):
        def __init__(self, function):
            self.function = function

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.function(*key)

            return ret

    return memodict(function)
