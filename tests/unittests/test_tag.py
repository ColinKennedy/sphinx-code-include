#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import test_code_include


class Linking(test_code_include.Linking):
    @staticmethod
    def _get_fake_project_method():
        return [u":obj:`fake_project.basic.MyKlass.get_method`"]


class RenderText(test_code_include.RenderText):
    @staticmethod
    def _get_fake_project_method():
        return [u":obj:`fake_project.basic.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_class():
        return [u":obj:`fake_project.basic.MyKlass`"]

    @staticmethod
    def _get_fake_project_function():
        return [u":obj:`fake_project.basic.set_function_thing`"]

    @staticmethod
    def _get_fake_project_private_function():
        return [u":obj:`fake_project.basic._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_module():
        return [u":obj:`fake_project.basic`"]


class RenderTextNested(test_code_include.RenderTextNested):
    @staticmethod
    def _get_fake_project_nested_method():
        return [u":obj:`fake_project.nested_folder.another.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_nested_class():
        return [u":obj:`fake_project.nested_folder.another.MyKlass`"]

    @staticmethod
    def _get_fake_project_nested_function():
        return [u":obj:`fake_project.nested_folder.another.set_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_private_function():
        return [u":obj:`fake_project.nested_folder.another._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_module():
        return [u":obj:`fake_project.nested_folder.another`"]


class Options(test_code_include.Options):
    @staticmethod
    def _get_fake_project_method():
        return [u":obj:`fake_project.basic.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_function():
        return [u":obj:`fake_project.basic.set_function_thing`"]
