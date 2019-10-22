#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Useful functions that other testing modules use."""

import warnings

from six.moves import mock
from sphinx.ext import intersphinx

from code_include import extension
from code_include import helper


def make_mock_directive(content):
    """Create the main class which is translated and rendered as text.

    Args:
        content (list[str]):
            The lines that the user provides in a standard code-include block.

    Returns:
        :class:`code_include.extension`:
            The class that is later translated by Sphinx into HTML tags.

    """
    name = "code-include"
    arguments = []
    options = {}
    line_number = 11
    content_offset = 10
    block_text = (
        u".. code-include:: :meth:`ways.asdf.base.plugin.DataPlugin.get_hierarchy`\n"
    )
    state = mock.MagicMock()
    state_machine = mock.MagicMock()

    return extension.Directive(
        name,
        arguments,
        options,
        content,
        line_number,
        content_offset,
        block_text,
        state,
        state_machine,
    )


@helper.memoize
def load_cache(path):
    """Load some inventory file as raw data.

    Args:
        path (str):
            The absolute path where an inventory file can be found.

    Returns:
        dict[str, dict[str, tuple[str, str, str, str]]]:
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
        def warn(message):
            """Send a warning if bad-formatted text is encountered."""
            warnings.warn(message)

    return intersphinx.fetch_inventory(MockApplication(), "", path)


@helper.memoize
def load_cache_from_url(url):
    """Load some inventory file as raw data.

    Args:
        url (str):
            The website address that points to a objects.inv file.
            e.g. "https://foo_bar_name.readthedocs.io/en/latest/objects.inv".

    Returns:
        dict[str, dict[str, tuple[str, str, str, str]]]:
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
        def warn(message):
            """Send a warning if bad-formatted text is encountered."""
            warnings.warn(message)

    return intersphinx.fetch_inventory(MockApplication(), "", url)
