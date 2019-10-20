#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that tests different uses of the code-include directive."""

import json
import os
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

    #     def test_no_required_argument(self):
    #         pass
    #
    #     def test_no_unindent(self):
    #         pass

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_incorrect_namespace(self, _get_app_inventory, _reraise_exception):
        with open(
            os.path.join(_CURRENT_DIRECTORY, "example_cache.inv"), "r"
        ) as handler:
            data = json.load(handler)

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True

        name = "code-include"
        arguments = []
        options = {}
        # content = StringList(
        #     [u':meth:`ways.asdf.base.plugin.DataPlugin.get_hierarchy`'],
        #     items=[(u'/home/selecaoone/repositories/test_project/source/index.rst', 10)],
        # )
        content = [u":meth:`path.that.does.not.exist`"]
        line_number = 11
        content_offset = 10
        block_text = u".. code-include:: :meth:`ways.asdf.base.plugin.DataPlugin.get_hierarchy`\n"
        state = mock.MagicMock()
        state_machine = mock.MagicMock()

        directive = extension.Directive(
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

        with self.assertRaises(error_classes.MissingNamespace):
            directive.run()

    # @mock.patch("code_include.source_code._get_app_inventory")
    # def test_basic(self, _get_app_inventory):
    #     with open(
    #         os.path.join(_CURRENT_DIRECTORY, "example_cache.inv"), "r"
    #     ) as handler:
    #         data = json.load(handler)
    #
    #     _get_app_inventory.return_value = data
    #
    #     name = "code-include"
    #     arguments = []
    #     options = {}
    #     # content = StringList(
    #     #     [u':meth:`ways.asdf.base.plugin.DataPlugin.get_hierarchy`'],
    #     #     items=[(u'/home/selecaoone/repositories/test_project/source/index.rst', 10)],
    #     # )
    #     content = [u":meth:`ways.base.plugin.DataPlugin.get_hierarchy`"]
    #     line_number = 11
    #     content_offset = 10
    #     block_text = u".. code-include:: :meth:`ways.asdf.base.plugin.DataPlugin.get_hierarchy`\n"
    #     state = mock.MagicMock()
    #     state_machine = mock.MagicMock()
    #
    #     directive = extension.Directive(
    #         name,
    #         arguments,
    #         options,
    #         content,
    #         line_number,
    #         content_offset,
    #         block_text,
    #         state,
    #         state_machine,
    #     )
    #
    #     nodes = directive.run()
    #     self.assertNotEqual([], nodes)


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
