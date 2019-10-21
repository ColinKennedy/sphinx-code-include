#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests that access content outside of this repository."""

import textwrap
import unittest

from six.moves import mock

from .. import common


class Reader(unittest.TestCase):
    """Check that external queries work."""

    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_app_inventory")
    def test_url(self, _get_app_inventory, _get_source_code_from_object, _get_source_module_data):
        """Get the source-code of some project from a URL."""
        path = "https://ways.readthedocs.io/en/latest/objects.inv"
        _get_app_inventory.return_value = common.load_cache_from_url(path)
        _get_source_module_data.return_value = (
            "https://ways.readthedocs.io/en/latest/_modules/ways/base/plugin.html",
            "DataPlugin",
        )
        _get_source_code_from_object.return_value = ""

        expected = textwrap.dedent(
            """\
            class DataPlugin(Plugin):

                '''An add-on that was made from a serialized file (JSON/YAML/etc).

                This class behaves exactly like a regular Plugin object and is stored
                in the same space as Plugin objects.

                DataPlugin does not add itself to the cache automatically. It is the
                responsibility of some other class/function to register it to Ways.

                We do this so that we can have better control over the DataPlugin's args
                and its assignment before it hits the cache.

                '''

                add_to_registry = False

                def __init__(self, name, sources, info, assignment):
                    '''Create the object and set its sources.

                    Args:
                        sources (list[str]): The location(s) that defined this Plugin.
                        info (dict[str]): The information that came from a JSON or YAML file
                                          which sets the base settings of the object.
                        assignment (str): The grouping location where this Plugin will go.
                                          This assignment must be the same as the Context
                                          that this Plugin is meant for.

                    Raises:
                        ValueError: If there are missing keys in data that this class needs.

                    '''
                    missing_required_keys = set(self._required_keys()) - set(info.keys())
                    if missing_required_keys:
                        raise ValueError('Info: "{info}" is missing keys, "{keys}".'
                                         ''.format(info=info, keys=missing_required_keys))

                    # Give this plugin a UUID if none was given, for us
                    # Data is assumed to be a core.classes.dict_class.ReadOnlyDict so we
                    # try to unlock it, here. If it's not a custom dict, just let it pass
                    #
                    try:
                        is_settable = info.settable
                        info.settable = True
                    except AttributeError:
                        pass

                    info.setdefault('uuid', str(uuid.uuid4()))

                    try:
                        info.settable = is_settable
                    except AttributeError:
                        pass

                    self.name = name
                    self._info = info
                    self.sources = tuple(sources)
                    self._data = self._info.get('data', dict())
                    self.assignment = assignment

                    super(DataPlugin, self).__init__()

                @classmethod
                def _required_keys(cls):
                    '''tuple[str]: Keys that must be set in our Plugin.'''
                    return ('hierarchy', )

                def is_path(self):
                    '''If the mapping is a filepath or None if unsure.

                    Returns:
                        bool or NoneType: If the mapping is a path to a file/folder on disk.

                    '''
                    try:
                        return self._info['path']
                    except KeyError:
                        return None

                def get_assignment(self):
                    '''str: Where this Plugin lives in Ways, along with its hierarchy.'''
                    return self.assignment

                def get_groups(self):
                    '''Get the groups that this Plugin evaluates onto.

                    Note:
                        The term 'groups' is not the same as the assignment of a Plugin.
                        They are two different things.

                    Returns:
                        tuple[str]: The groups.

                    '''
                    value = check.force_itertype(self._info.get('groups', ('*', )), itertype=tuple)
                    is_empty = not [val for val in value if val.strip()]
                    if is_empty:
                        value = ('*', )
                    return value

                def get_hierarchy(self):
                    '''tuple[str] or str: The location that this Plugin exists within.'''
                    return self._info['hierarchy']

                def get_mapping(self):
                    '''str: The physical location of this Plugin (on the filesystem).'''
                    try:
                        return self._info['mapping']
                    except KeyError:
                        return ''

                def get_mapping_details(self):
                    '''dict[str]: Information about the mapping, if needed.'''
                    return self._info.get('mapping_details', dict())

                def get_max_folder(self):
                    '''str: The furthest location up that this plugin can navigate to.'''
                    return self._info.get('max_folder', '')

                def get_platforms(self):
                    '''set[str]: The platforms that this Plugin is allowed to run on.'''
                    platforms = ways.get_known_platfoms()
                    return set(self._info.get('platforms', platforms))

                def get_uses(self):
                    '''tuple[str]: The Context hierarchies this instance depends on.'''
                    return self._info.get('uses', tuple())

                def get_uuid(self):
                    '''str: A unique ID for this plugin.'''
                    return self._info.get('uuid', '')

                def __repr__(self):
                    '''str: The information needed to reproduce this instance.'''
                    return '{cls_}(sources={sources!r}, data={data})'.format(
                        cls_=self.__class__.__name__,
                        sources=self.sources,
                        data=dict(self._info))

                def __str__(self):
                    '''str: A more concise print-out of this instance.'''
                    return '{cls_}(hierarchy={hierarchy}, sources={sources!r})'.format(
                        cls_=self.__class__.__name__,
                        hierarchy=self.get_hierarchy(),
                        sources=self.sources)"""
        )

        content = [":class:`ways.base.plugin.DataPlugin`"]
        directive = common.make_mock_directive(content)
        nodes = directive.run()

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())

    @mock.patch("code_include.source_code._get_app_inventory")
    def test_import(self, _get_app_inventory):
        """Get the source-code of an importable object."""
        _get_app_inventory.return_value = {"non-empty": {"information": tuple()}}

        expected = textwrap.dedent(
            '''\
            def join(a, *p):
                """Join two or more pathname components, inserting '/' as needed.
                If any component is an absolute path, all previous path components
                will be discarded.  An empty last part will result in a path that
                ends with a separator."""
                path = a
                for b in p:
                    if b.startswith('/'):
                        path = b
                    elif path == '' or path.endswith('/'):
                        path +=  b
                    else:
                        path += '/' + b
                return path'''
        )

        content = [":func:`os.path.join`"]
        directive = common.make_mock_directive(content)
        nodes = directive.run()

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())
