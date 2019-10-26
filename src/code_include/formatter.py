#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A helper module that converts strings for this extension."""

import re
import sys

_DIRECTIVE_EXPRESSION = re.compile(r":(?P<directive>[\w:]+):`(?P<namespace>[\w\.]+)`")
_NAMED_DIRECTIVE_EXPRESSION = re.compile(
    r":(?P<directive>[\w:]+):`(?P<location>[\w+\._]+)\s+<(?P<namespace>[\w\.]+)>`"
)


def get_converted_directive(directive):
    """Change the user-provided directive target to one that this extension understands.

    The goal of this function is to always return a target that one
    might find in an intersphinx objects.inv inventory file.

    To get a list of the keys in your object, run this code

    ::

        python -m sphinx.ext.intersphinx https://your_package.readthedocs.io/en/latest

    That will print every key that the project uses. Theoretically, this
    function should be able to support every key found.

    Args:
        directive (str):
            Some user-provided target that the user writes in
            documentation, like ":attr:", ":func:", etc.

    Returns:
        str:
            The converted directive. If no directive is found, then
            return an empty string.

    """
    directive = directive.strip(":")

    # TODO : There's probably a better way to map these values.
    # TODO : Double-check that this is everything that I need
    inventory_directive_mapper = {
        "attr": "py:attribute",
        "class": "py:class",
        "func": "py:function",
        "meth": "py:method",
        "mod": "py:module",
    }

    try:
        return inventory_directive_mapper[directive]
    except KeyError:
        return ""


def get_raw_content(text):
    """Split some code-include target into its most important parts.

    Args:
        text (str):
            The user-provided target from a `.. code-include::` directive.
            Example: ":func:`ways.base.plugin.get_assignment`".

    Raises:
        RuntimeError:
            If the given text wasn't a valid target convention.

    Returns:
        tuple[str, str]:
            The target's type + the Python namespace for where the object lives.

    """
    match = _DIRECTIVE_EXPRESSION.match(text) or _NAMED_DIRECTIVE_EXPRESSION.match(text)

    if not match:
        patterns = [_DIRECTIVE_EXPRESSION.pattern, _NAMED_DIRECTIVE_EXPRESSION.pattern]

        raise RuntimeError(
            'text "{text}" is not valid. Text must match one of these patterns: '
            '[{patterns}]".'.format(text=text, patterns="\n".join(sorted(patterns)))
        )

    return match.group("directive"), match.group("namespace")


def unindent_outer_whitespace(text):
    r"""Unindent some text until the outter-most line has no leading whitespace.

    Example:
        >>> code = \
        >>> '''
        >>>         def foo():
        >>>             pass

        >>> '''

        >>> print(unindent_outer_whitespace(code))
        >>> # Result:
        >>> # def foo():
        >>> #     pass

    Args:
        text (str):
            The text to remove unnecessary whitespace from.

    Returns:
        str: The converted text.

    """
    indent_size = sys.maxsize
    lines = text.splitlines()

    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())

        if indent < indent_size:
            indent_size = indent

    if indent_size != sys.maxsize:
        lines = [line[indent_size:] for line in lines]

    return "\n".join(lines)
