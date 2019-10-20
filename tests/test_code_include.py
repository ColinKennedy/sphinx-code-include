#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO : Consider reducing the inputs for test functinos
"""The main module that tests different uses of the code-include directive."""
import json
import os
import textwrap
import unittest
import warnings

from code_include import error_classes
from code_include import extension
from code_include import helper
from code_include import source_code
from six.moves import mock
from sphinx.ext import intersphinx


_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Inputs(unittest.TestCase):
    """Check that different input to the code-include directive works as-expected."""

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _test(self, content, exception_class, _get_app_inventory, _reraise_exception):
        data = _load_cache("fake_project", "objects.inv")

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        directive = _make_mock_directive(content)

        with self.assertRaises(exception_class):
            directive.run()

    def test_no_required_argument(self):
        self._test([""], error_classes.MissingContent)

    def test_incorrect_namespace(self):
        self._test(
            [u":meth:`path.that.does.not.exist`"], error_classes.MissingNamespace
        )

    def test_incorrect_directive_target(self):
        self._test(
            [u":nonexistent:tag:`some.module.that.may.exist`"],
            error_classes.MissingDirective,
        )


class RenderText(unittest.TestCase):
    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_get_from_html(self, _get_app_inventory, _get_source_module_data):
        data = _load_cache("fake_project", "objects.inv")

        _get_app_inventory.return_value = data
        _get_source_module_data.return_value = (
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
        directive = _make_mock_directive(content)

        nodes = directive.run()
        expected = textwrap.dedent(
            '''\
            def get_method(self):
                """int: Get some value."""
                return 8'''
        )

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())

    @mock.patch("code_include.extension.Directive._needs_unindent")
    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_no_unindent(
        self, _get_app_inventory, _get_source_module_data, _needs_unindent
    ):
        _needs_unindent.return_value = False
        data = _load_cache("fake_project", "objects.inv")

        _get_app_inventory.return_value = data
        _get_source_module_data.return_value = (
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
        directive = _make_mock_directive(content)

        nodes = directive.run()
        expected = '''\
    def get_method(self):
        """int: Get some value."""
        return 8'''

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())

    def test_attribute(self):
        pass

    def test_class(self):
        pass

    def test_class_attribute(self):
        pass

    def test_function(self):
        pass


@helper.memoize
def _load_cache(*paths):
    class MockConfiguration(object):
        intersphinx_timeout = None  # type: int
        tls_verify = False

    class MockApplication(object):
        srcdir = ""
        config = MockConfiguration()

        def warn(self, msg):
            warnings.warn(msg)

    return intersphinx.fetch_inventory(
        MockApplication(), "", os.path.join(_CURRENT_DIRECTORY, *paths)
    )


def _make_mock_directive(content):
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
