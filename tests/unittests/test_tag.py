#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module checks that :obj: works as expected.

It works by re-using almost all of the code from `test_code_include` and
just changes a few functions to test for the :obj: tag.

"""

from . import test_code_include


class Linking(test_code_include.Linking):
    """A class that checks if linking to source code and documentation works."""

    @staticmethod
    def _get_fake_project_method() -> list[str]:
        return [":obj:`fake_project.basic.MyKlass.get_method`"]


class RenderText(test_code_include.RenderText):
    """A class that checks to make sure projects get and return the right code."""

    @staticmethod
    def _get_fake_project_method() -> list[str]:
        return [":obj:`fake_project.basic.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_class() -> list[str]:
        return [":obj:`fake_project.basic.MyKlass`"]

    @staticmethod
    def _get_fake_project_function() -> list[str]:
        return [":obj:`fake_project.basic.set_function_thing`"]

    @staticmethod
    def _get_fake_project_private_function() -> list[str]:
        return [":obj:`fake_project.basic._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_module() -> list[str]:
        return [":obj:`fake_project.basic`"]


class RenderTextNested(test_code_include.RenderTextNested):
    """Make sure that nested HTML rendering works as expected."""

    @staticmethod
    def _get_fake_project_nested_method() -> list[str]:
        return [":obj:`fake_project.nested_folder.another.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_nested_class() -> list[str]:
        return [":obj:`fake_project.nested_folder.another.MyKlass`"]

    @staticmethod
    def _get_fake_project_nested_function() -> list[str]:
        return [":obj:`fake_project.nested_folder.another.set_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_private_function() -> list[str]:
        return [":obj:`fake_project.nested_folder.another._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_module() -> list[str]:
        return [":obj:`fake_project.nested_folder.another`"]


class Options(test_code_include.Options):
    """Make sure code-include directive options work for :obj: tags."""

    @staticmethod
    def _get_fake_project_method() -> list[str]:
        return [":obj:`fake_project.basic.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_function() -> list[str]:
        return [":obj:`fake_project.basic.set_function_thing`"]
