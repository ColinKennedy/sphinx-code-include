#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO : Consider reducing the inputs for test functinos
"""The main module that tests different uses of the code-include directive."""
import json
import os
import textwrap
import unittest

from code_include import error_classes
from code_include import extension
from code_include import source_code
from six.moves import mock


_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Inputs(unittest.TestCase):
    """Check that various input to the code-include directive works as-expected."""

    def test_empty(self):
        """Fail any empty code-include directive."""

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_no_required_argument(self, _get_app_inventory, _reraise_exception):
        data = _load_cache("example_cache.inv")

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        content = ['']
        directive = _make_mock_directive(content)

        with self.assertRaises(error_classes.MissingNamespace):
            directive.run()

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_incorrect_namespace(self, _get_app_inventory, _reraise_exception):
        data = _load_cache("example_cache.inv")

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        content = [u":meth:`path.that.does.not.exist`"]
        directive = _make_mock_directive(content)

        with self.assertRaises(error_classes.MissingNamespace):
            directive.run()

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_incorrect_directive_target(self, _get_app_inventory, _reraise_exception):
        data = _load_cache("example_cache.inv")

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        content = [u":nonexistent:tag:`some.module.that.may.exist`"]
        directive = _make_mock_directive(content)

        with self.assertRaises(error_classes.MissingDirective):
            directive.run()


class RenderText(unittest.TestCase):
    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_get_from_html(self, _get_app_inventory, _get_source_module_data):
        data = _load_cache("example_cache.inv")

        _get_app_inventory.return_value = data
        _get_source_module_data.return_value = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "ways",
                "base",
                "plugin.html",
            ),
            "DataPlugin.get_hierarchy",
        )

        content = [u":meth:`ways.base.plugin.DataPlugin.get_hierarchy`"]
        directive = _make_mock_directive(content)

        nodes = directive.run()
        expected = textwrap.dedent(
            """\
            def get_hierarchy(self):
                '''tuple[str] or str: The location that this Plugin exists within.'''
                return self._info['hierarchy']"""
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
        data = _load_cache("example_cache.inv")

        _get_app_inventory.return_value = data
        _get_source_module_data.return_value = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "ways",
                "base",
                "plugin.html",
            ),
            "DataPlugin.get_hierarchy",
        )

        content = [u":meth:`ways.base.plugin.DataPlugin.get_hierarchy`"]
        directive = _make_mock_directive(content)

        nodes = directive.run()
        expected = """\
    def get_hierarchy(self):
        '''tuple[str] or str: The location that this Plugin exists within.'''
        return self._info['hierarchy']"""

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())


# class Permutations(unittest.TestCase):
#     def test_class(self):
#         pass
#
#     def test_method(self):
#         pass
#
#     def test_function(self):
#         pass
#
#     def test_attribute(self):
#         pass


def _load_cache(*paths):
    with open(os.path.join(_CURRENT_DIRECTORY, *paths), "r") as handler:
        return json.load(handler)


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
