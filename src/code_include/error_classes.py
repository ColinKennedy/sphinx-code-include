#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of classes made for error/warning reporting."""


class MissingContent(Exception):
    """If a user creates a code-include directive with no target."""

    pass


class MissingNamespace(Exception):
    """If the user specifies a missing target.

    For example, the user might write a target like :mod:`foo`. If "foo"
    is missing across ":mod:" locations for all Sphinx projects found in
    the interspinx inventory, this exception raises.

    """

    pass


class MissingTag(Exception):
    """If the user specifies a missing directive.

    For example, the user might write a target like :mod:`foo`. If
    ":mod:" is missing across all Sphinx projects in the interspinx
    inventory, this exception raises.

    """

    pass


class NotFoundFile(Exception):
    """An class to describe a local intersphinx project that does not exist."""

    pass


class NotFoundUrl(Exception):
    """An class to describe a URL intersphinx project that does not exist."""

    pass
