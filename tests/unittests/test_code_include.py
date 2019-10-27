#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO : Consider reducing the inputs for test functinos
"""The main module that tests different uses of the code-include directive."""

import os
import textwrap
import unittest

from six.moves import mock

from code_include import error_classes
from code_include import extension

from .. import common

_CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Inputs(unittest.TestCase):
    """Check that different input to the code-include directive works as-expected."""

    @mock.patch("code_include.extension.Directive._reraise_exception")
    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _test(
        self,
        content,
        exception_class,
        _get_app_inventory,
        _get_source_code_from_object,
        _reraise_exception,
    ):
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
        data = common.load_cache(os.path.join(_CURRENT_DIRECTORY, "fake_project", "objects.inv"))

        _get_app_inventory.return_value = data
        _reraise_exception.return_value = True
        _get_source_code_from_object.return_value = ""

        directive = common.make_mock_directive(content)

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
            error_classes.MissingTag,
        )

    def test_incorrect_namespace(self):
        """Check that a valid tag but incorrect namespace raises the expected exception."""
        self._test(  # pylint: disable=no-value-for-parameter
            [u":meth:`path.that.does.not.exist`"], error_classes.MissingNamespace
        )


class ContentsStore(unittest.TestCase):
    """A class that provides input text for other unittest classes.

    The text in this class mimics what the user would write in a regular
    code-include block.

    """

    @staticmethod
    def _get_fake_project_class():
        return [u":class:`fake_project.basic.MyKlass`"]

    @staticmethod
    def _get_fake_project_function():
        return [u":func:`fake_project.basic.set_function_thing`"]

    @staticmethod
    def _get_fake_project_module():
        return [u":mod:`fake_project.basic`"]

    @staticmethod
    def _get_fake_project_nested_class():
        return [u":class:`fake_project.nested_folder.another.MyKlass`"]

    @staticmethod
    def _get_fake_project_nested_function():
        return [u":func:`fake_project.nested_folder.another.set_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_private_function():
        return [u":func:`fake_project.nested_folder.another._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_nested_method():
        return [u":meth:`fake_project.nested_folder.another.MyKlass.get_method`"]

    @staticmethod
    def _get_fake_project_nested_module():
        return [u":mod:`fake_project.nested_folder.another`"]

    @staticmethod
    def _get_fake_project_private_function():
        return [u":func:`fake_project.basic._set_private_function_thing`"]

    @staticmethod
    def _get_fake_project_method():
        return [u":meth:`fake_project.basic.MyKlass.get_method`"]


class Linking(ContentsStore):
    """A class that checks if linking to source code and documentation works."""

    @staticmethod
    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _get_nodes(
        data, content, _inventory, _get_from_object, _get_source_module_data
    ):
        cache = common.load_cache(os.path.join(_CURRENT_DIRECTORY, "fake_project", "objects.inv"))

        _inventory.return_value = cache
        _get_source_module_data.return_value = data
        _get_from_object.return_value = ""

        directive = common.make_mock_directive(content)

        return directive.run()

    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.extension.Directive._is_link_requested")
    @mock.patch("code_include.extension.Directive._needs_unindent")
    def test_link_to_documentation(
        self,
        _needs_unindent,
        _is_link_requested,
        _get_source_code_from_object,
    ):
        """Link to the original page where Python source-code was found.

        Args:
            _needs_unindent (:class:`mock.mock.MagicMock`):
                The patched function that controls indentation of code-include.
            _is_link_requested (:class:`mock.mock.MagicMock`):
                This adds a hyperlink to the original Python documentation.
            _get_source_code_from_object (:class:`mock.mock.MagicMock`):
                Disable reading from source-code. This forces
                sphinx-code-include to read from a Sphinx inventory
                file.

        """
        _needs_unindent.return_value = False
        _is_link_requested.return_value = True
        _get_source_code_from_object.return_value = ""

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
        content = self._get_fake_project_method()
        nodes = self._get_nodes(data, content)  # pylint: disable=no-value-for-parameter

        self.assertEqual(2, len(nodes))
        self.assertTrue(any(node for node in nodes if isinstance(
            node,
            extension._DocumentationHyperlink,  # pylint: disable=protected-access
        )))

    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.extension.Directive._is_source_requested")
    @mock.patch("code_include.extension.Directive._needs_unindent")
    def test_link_to_source(
        self,
        _needs_unindent,
        _is_source_requested,
        _get_source_code_from_object,
    ):
        """Link to the original page where Python source-code was found.

        Args:
            _needs_unindent (:class:`mock.mock.MagicMock`):
                The patched function that controls indentation of code-include.
            _is_source_requested (:class:`mock.mock.MagicMock`):
                This adds a hyperlink to the original Python source-code.
            _get_source_code_from_object (:class:`mock.mock.MagicMock`):
                Disable reading from source-code. This forces
                sphinx-code-include to read from a Sphinx inventory
                file.

        """
        _needs_unindent.return_value = False
        _is_source_requested.return_value = True
        _get_source_code_from_object.return_value = ""

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
        content = self._get_fake_project_method()
        nodes = self._get_nodes(data, content)  # pylint: disable=no-value-for-parameter

        self.assertEqual(2, len(nodes))
        self.assertTrue(any(node for node in nodes if isinstance(
            node,
            extension._SourceCodeHyperlink,  # pylint: disable=protected-access
        )))


class _Common(ContentsStore):
    """A base class which is used by sub-classes to make tests more concise."""

    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_app_inventory")
    def _test(
        self, data, content, expected, _inventory, _get_from_object, _get_source_module_data
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
            _inventory (:class:`mock.mock.MagicMock`):
                The function that's normally used to query a Sphinx
                project's inventory to find every HTML file-path and
                tag-able header.
            _get_source_module_data (:class:`mock.mock.MagicMock`):
                A function that is mocked so that we can skip some of
                the less important tag-parsing functions and get to the
                point of this function - testing generated source-code.

        """
        cache = common.load_cache(os.path.join(_CURRENT_DIRECTORY, "fake_project", "objects.inv"))

        _inventory.return_value = cache
        _get_source_module_data.return_value = data
        _get_from_object.return_value = ""

        directive = common.make_mock_directive(content)
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
        content = self._get_fake_project_method()

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
        content = self._get_fake_project_class()

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
        content = self._get_fake_project_function()

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
        content = self._get_fake_project_private_function()

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

    def test_module(self):
        """Check that a module is read properly."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "basic.html",
            ),
            "",
        )
        content = self._get_fake_project_module()

        expected = textwrap.dedent(
            '''\
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-

            """A module that shows every type of documentable class / method / function.

            Attributes:
                ATTRIBUTE_VALUE (float):
                    Some number.

            """


            ATTRIBUTE_VALUE = 14.3


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
                    return 8


            class ParentClass(object):
                """The outter class.

                Attributes:
                    attribute_value (str):
                        Some string.

                """

                attribute_value = "tttt"

                class NestedClass(object):
                    """A class within a class.

                    Attributes:
                        attribute_value (str):
                            Some string.

                    """

                    attribute_value = "zzzzzzzzzzzzz"

                    @staticmethod
                    def get_staticmethod():
                        """int: Get some value."""
                        return 5

                    @classmethod
                    def get_classmethod(cls):
                        """int: Get some value."""
                        return 5

                    def get_method(self):
                        """int: Get some value."""
                        return 5

                @staticmethod
                def get_staticmethod():
                    """int: Get some value."""
                    return 6

                @classmethod
                def get_classmethod(cls):
                    """int: Get some value."""
                    return 6

                def get_method(self):
                    """int: Get some value."""
                    return 6


            def _set_private_function_thing(value, another):
                """Do something here."""
                # Do something with these values
                # and more comment text, here.
                #
                if value:
                    return 2

                # Another comment
                return 1


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


class RenderTextNested(_Common):
    """A class that checks to make sure projects get and return the right code."""

    def test_get_from_html(self):
        """Check that a basic HTML file can be read."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "nested_folder",
                "another.html",
            ),
            "MyKlass.get_method",
        )
        content = self._get_fake_project_nested_method()

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
                "nested_folder",
                "another.html",
            ),
            "MyKlass",
        )

        content = self._get_fake_project_nested_class()

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
                "nested_folder",
                "another.html",
            ),
            "set_function_thing",
        )
        content = self._get_fake_project_nested_function()

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
                "nested_folder",
                "another.html",
            ),
            "_set_private_function_thing",
        )
        content = self._get_fake_project_nested_private_function()

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

    def test_module(self):
        """Check that a module is read properly."""
        data = (
            os.path.join(
                _CURRENT_DIRECTORY,
                "fake_project",
                "_modules",
                "fake_project",
                "nested_folder",
                "another.html",
            ),
            "",
        )

        content = self._get_fake_project_nested_module()

        expected = textwrap.dedent(
            '''\
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-

            """A module that shows every type of documentable class / method / function.

            Attributes:
                ATTRIBUTE_VALUE (float):
                    Some number.

            """


            ATTRIBUTE_VALUE = 14.3


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
                    return 8


            class ParentClass(object):
                """The outter class.

                Attributes:
                    attribute_value (str):
                        Some string.

                """

                attribute_value = "tttt"

                class NestedClass(object):
                    """A class within a class.

                    Attributes:
                        attribute_value (str):
                            Some string.

                    """

                    attribute_value = "zzzzzzzzzzzzz"

                    @staticmethod
                    def get_staticmethod():
                        """int: Get some value."""
                        return 5

                    @classmethod
                    def get_classmethod(cls):
                        """int: Get some value."""
                        return 5

                    def get_method(self):
                        """int: Get some value."""
                        return 5

                @staticmethod
                def get_staticmethod():
                    """int: Get some value."""
                    return 6

                @classmethod
                def get_classmethod(cls):
                    """int: Get some value."""
                    return 6

                def get_method(self):
                    """int: Get some value."""
                    return 6


            def _set_private_function_thing(value, another):
                """Do something here."""
                # Do something with these values
                # and more comment text, here.
                #
                if value:
                    return 2

                # Another comment
                return 1


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


class Options(_Common):
    """A generic class that tests options that users can add to a code-include directive."""

    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.extension.Directive._needs_unindent")
    def test_no_unindent(self, _needs_unindent, _get_source_code_from_object):
        """Check that code-include doesn't remove leading whitespace, when selected.

        Args:
            _needs_unindent (:class:`mock.mock.MagicMock`):
                The patched function that controls indentation of code-include.

        """
        _needs_unindent.return_value = False
        _get_source_code_from_object.return_value = ""

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
        content = self._get_fake_project_method()

        expected = '''\
    def get_method(self):
        """int: Get some value."""
        return 8'''

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter

    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_page_preprocessor")
    def test_preprocessor(self, _get_page_preprocessor, _get_source_code_from_object):
        """Check that the optional user-configuration function works correctly."""
        def _remove_comments_and_docstrings(node):
            for tag in node.find_all("span", {"class": ["c1", "sd"]}):
                tag.decompose()

        _get_page_preprocessor.return_value = _remove_comments_and_docstrings
        _get_source_code_from_object.return_value = ""

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
        content = self._get_fake_project_function()

        expected = '''\
def set_function_thing(value, another):
    
    
    
    
    if value:
        return 2

    
    return 1'''

        self._test(data, content, expected)  # pylint: disable=no-value-for-parameter
