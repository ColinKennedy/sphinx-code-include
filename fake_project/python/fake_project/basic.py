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
    return 1
