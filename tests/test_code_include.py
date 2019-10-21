#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO : Consider reducing the inputs for test functinos
"""The main module that tests different uses of the code-include directive."""

import os
import textwrap
import unittest
import warnings

from six.moves import mock
from sphinx.ext import intersphinx

from code_include import error_classes
from code_include import extension
from code_include import helper

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Inputs(unittest.TestCase):
    """Check that different input to the code-include directive works as-expected."""

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _test(self, content, exception_class, _get_app_inventory, _reraise_exception):
        """A generic function that checks a code-include directive for issues.

        Args:
            content (list[str]):
                The lines that the user provides in a standard code-include block.
            exception_class (Exception):
                The exception that should be raised, when given `content`.
            _get_app_inventory (:class:`mock.mock.MagicMock`):
                The function that's normally used to query a Sphinx
                project's inventory to find every HTML file-path and
                tag-able header.
            _reraise_exception (:class:`mock.mock.MagicMock`):
                A function that must be set to return `True` so that
                this test will forcibly raise the found exception.

        """
        data = _load_cache("fake_project", "objects.inv")

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        directive = _make_mock_directive(content)

        with self.assertRaises(exception_class):
            directive.run()

    def test_no_required_argument(self):
        """Check that missing content raises the expected exception."""
        self._test(  # pylint: disable=no-value-for-parameter
            [""], error_classes.MissingContent
        )

    def test_incorrect_directive_target(self):
        """Check that a bad tag like ":foo:" raises the expected exception."""
        self._test(  # pylint: disable=no-value-for-parameter
            [u":nonexistent:tag:`some.module.that.may.exist`"],
            error_classes.MissingDirective,
        )

    def test_incorrect_namespace(self):
        """Check that a valid tag but incorrect namespace raises the expected exception."""
        self._test(  # pylint: disable=no-value-for-parameter
            [u":meth:`path.that.does.not.exist`"], error_classes.MissingNamespace
        )


class _Common(unittest.TestCase):
    """A base class which is used by sub-classes to make tests more concise."""

    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _test(
        self, data, content, expected, _get_app_inventory, _get_source_module_data
    ):
        """A generic function that tests a code-include directive for some text.

        Args:
            data (tuple[str, str]):
                The absolute path to an HTML file and the "#foo" tag that
                would normally be used as a permalink to some header in the
                HTML file.
            content (list[str]):
                The lines that the user provides in a standard code-include block.
            expected (str):
                The converted source-code text that will be tested for.
            _get_app_inventory (:class:`mock.mock.MagicMock`):
                The function that's normally used to query a Sphinx
                project's inventory to find every HTML file-path and
                tag-able header.
            _get_source_module_data (:class:`mock.mock.MagicMock`):
                A function that is mocked so that we can skip some of
                the less important tag-parsing functions and get to the
                point of this function - testing generated source-code.

        """
        cache = _load_cache("fake_project", "objects.inv")

        _get_app_inventory.return_value = cache
        _get_source_module_data.return_value = data

        directive = _make_mock_directive(content)
        nodes = directive.run()

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())


class RenderText(_Common):
    """A class that checks to make sure projects get and return the right code."""

    def test_get_from_html(self):
        """Check that a basic HTML file can be read."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "MyKlass.get_method",
        )
        content = [u":meth:`fake_project.basic.MyKlass.get_method`"]

        expected = textwrap.dedent(
            '''\
            def get_method(self):
                """int: Get some value."""
                return 8'''
        )

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter

    def test_class(self):
        """Check that a class is read properly."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "MyKlass",
        )
        content = [u":class:`fake_project.basic.MyKlass`"]

        expected = textwrap.dedent(
            '''\
            class MyKlass(object):
                """A class that does something.

                Multi-line information here.

                Attributes:
                    attribute_value (str):
                        Some string.

                """

                attribute_value = "asdfasdf"

                def __init__(self, value):
                    """Create this instance."""
                    # A comment that should show up in the unittest's results
                    super(MyKlass, self).__init__()

                @staticmethod
                def get_staticmethod():
                    """int: Get some value."""
                    return 8

                @classmethod
                def get_classmethod(cls):
                    """int: Get some value."""
                    return 8

                def get_method(self):
                    """int: Get some value."""
                    return 8'''
        )

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter

    def test_function(self):
        """Check that a module's function is read properly."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "set_function_thing",
        )
        content = [u":func:`fake_project.basic.set_function_thing`"]

        expected = textwrap.dedent(
            '''\
            def set_function_thing(value, another):
                """Do something here."""
                # Do something with these values
                # and more comment text, here.
                #
                if value:
                    return 2

                # Another comment
                return 1'''
        )

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter

    def test_private_function(self):
        """Check that a module's function is read properly."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "_set_private_function_thing",
        )
        content = [u":func:`fake_project.basic._set_private_function_thing`"]

        expected = textwrap.dedent(
            '''\
            def _set_private_function_thing(value, another):
                """Do something here."""
                # Do something with these values
                # and more comment text, here.
                #
                if value:
                    return 2

                # Another comment
                return 1'''
        )

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter

    # def test_module(self):
    #     """Check that a module is read properly."""
    #     pass


class Options(_Common):
    """A generic class that tests options that users can add to a code-include directive."""

    @mock.patch("code_include.extension.Directive._needs_unindent")
    def test_no_unindent(self, _needs_unindent):
        """Check that code-include doesn't remove leading whitespace, when selected.

        Args:
            _needs_unindent (:class:`mock.mock.MagicMock`):
                The patched function that controls indentation of code-include.

        """
        _needs_unindent.return_value = False

        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "MyKlass.get_method",
        )
        content = [u":meth:`fake_project.basic.MyKlass.get_method`"]
        expected = '''\
    def get_method(self):
        """int: Get some value."""
        return 8'''

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter


@helper.memoize
def _load_cache(*paths):
    """Load some inventory file as raw data.

    Args:
        *paths (iter[str]):
            The paths, relative to this test file's directory, where an
            inventory file can be found.

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

    return intersphinx.fetch_inventory(
        MockApplication(), "", os.path.join(_CURRENT_DIRECTORY, *paths)
    )


def _make_mock_directive(content):
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
