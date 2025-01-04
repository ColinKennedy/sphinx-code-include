#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Useful functions that other testing modules use."""

from __future__ import annotations

import typing
import warnings
from unittest import mock

from docutils import statemachine
from sphinx import application
from sphinx.ext import intersphinx

from code_include import extension
from code_include import helper

if typing.TYPE_CHECKING:
    from sphinx.util.typing import Inventory


def make_mock_directive(
    content: list[str],
    options: typing.Optional[dict[str, object]] = None,
) -> extension.Directive:
    """Create the main class which is translated and rendered as text.

    Args:
        content:
            The lines that the user provides in a standard code-include block.
        options:
            Directive modifiers (e.g. ``{"fallback-text": "foo bar"}``).

    Returns:
        The class that is later translated by Sphinx into HTML tags.

    """
    options = options or {}

    name = "code-include"
    arguments: list[str] = []
    line_number = 11
    content_offset = 10
    block_text = ""
    state = mock.MagicMock()
    state_machine = mock.MagicMock()

    return extension.Directive(
        name,
        arguments,
        options,
        statemachine.StringList(content),
        line_number,
        content_offset,
        block_text,
        state,
        state_machine,
    )


@helper.memoize
def load_cache(path: str) -> Inventory:
    """Load some inventory file as raw data.

    Args:
        path:
            The absolute path where an inventory file can be found.

    Returns:
        Each directive target type, its namespace, and it's file-path/URL information.
        e.g. {
            "py:method": {
                "fake_project.basic.MyKlass.get_method": (
                    "fake_project",
                    "",
                    "api/fake_project.html#fake_project.basic.MyKlass.get_method",
                    "-",
                )
            }
        }

    """

    class MockConfiguration(object):  # pylint: disable=too-few-public-methods
        """A fake set of settings for intersphinx to pass-through."""

        intersphinx_timeout = None  # type: int
        tls_verify = False

    class MockApplication(object):  # pylint: disable=too-few-public-methods
        """A fake state machine for intersphinx to consume and pass-through."""

        srcdir = ""
        config = MockConfiguration()

        @staticmethod
        def warn(message: str) -> None:
            """Send a warning if bad-formatted text is encountered."""
            warnings.warn(message)

    return intersphinx.fetch_inventory(
        typing.cast(application.Sphinx, MockApplication()),
        "",
        path,
    )


@helper.memoize
def load_cache_from_url(url: str) -> Inventory:
    """Load some inventory file as raw data.

    Args:
        url:
            The website address that points to a objects.inv file.
            e.g. "https://foo_bar_name.readthedocs.io/en/latest/objects.inv".

    Returns:
        Each directive target type, its namespace, and it's file-path/URL information.
        e.g. {
            "py:method": {
                "fake_project.basic.MyKlass.get_method": (
                    "fake_project",
                    "",
                    "api/fake_project.html#fake_project.basic.MyKlass.get_method",
                    "-",
                )
            }
        }

    """

    class MockConfiguration(object):  # pylint: disable=too-few-public-methods
        """A fake set of settings for intersphinx to pass-through."""

        intersphinx_timeout = None  # type: int
        tls_cacerts = ""  # Needed for Python 3.10+
        tls_verify = False
        user_agent = ""

    class MockApplication(object):  # pylint: disable=too-few-public-methods
        """A fake state machine for intersphinx to consume and pass-through."""

        srcdir = ""
        config = MockConfiguration()

        @staticmethod
        def warn(message: str) -> None:
            """Send a warning if bad-formatted text is encountered."""
            warnings.warn(message)

    return intersphinx.fetch_inventory(
        typing.cast(application.Sphinx, MockApplication()),
        "",
        url,
    )
