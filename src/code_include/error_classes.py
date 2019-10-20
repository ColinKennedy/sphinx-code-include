#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of classes which are used for error/warning reporting."""


class MissingContent(Exception):
    """If a user creates a code-include directive with no target."""

    pass


class MissingDirective(Exception):
    """If the user specifies a directive that couldn't be found.

    For example, the user might write a target like :mod:`foo`.
    If ":mod:" is missing across all Sphinx projects found in the
    interspinx inventory then this exception is raised.

    """

    pass


class MissingNamespace(Exception):
    """If the user specifies a target that couldn't be found.

    For example, the user might write a target like :mod:`foo`. If "foo"
    is missing across ":mod:" locations for all Sphinx projects found in
    the interspinx inventory then this exception is raised.

    """

    pass


class NotFoundFile(Exception):
    """An class to describe a local intersphinx project that does not exist."""

    pass


class NotFoundUrl(Exception):
    """An class to describe a URL intersphinx project that does not exist."""

    pass
