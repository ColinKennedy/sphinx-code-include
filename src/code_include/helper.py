#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extension-agnostic functions that other modules can freely use."""

from __future__ import annotations

import typing


class MemoDict(dict[typing.Any, typing.Any]):
    """A class that stores a function and caches each unique function call."""

    def __init__(self, function: typing.Callable[..., typing.Any]) -> None:
        """Keep track of a function so that we can call it later.

        Args:
            function: The callable function to remember.

        """
        super().__init__()

        self.function = function

    def __call__(self, *args: str) -> typing.Any:
        """Get data from this instance using ``args``.

        Args:
            args: Any data to query from.

        Returns:
            The result.

        """
        return self[args]

    def __missing__(self, key: str) -> typing.Any:
        """Pass ``key`` to the underlying function and call it from there.

        Args:
            key: The information to send to the function.

        """
        result = self.function(*key)
        self[key] = result

        return result


def memoize(function: typing.Callable[..., typing.Any]) -> MemoDict:
    """Wrap a function with this decorator to cache its results.

    Reference:
        http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/#c1

    Args:
        function:
            Some Python callable will become cache-able by this function.

    Returns:
        A per-function instance gets called only once for a set of
        arguments once.

    """
    return MemoDict(function)
