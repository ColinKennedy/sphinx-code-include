#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests that access content outside of this repository."""

import sys
import textwrap
import unittest

from six.moves import mock
from six.moves import urllib

from .. import common


def _skip_from_ssl_error(url):
    """bool: Check if the given URL can be reached."""
    # This function is mostly meant for pypy3
    try:
        from _cffi_ssl._stdssl import error
    except ImportError:
        return False

    try:
        return urllib.request.urlopen(url).getcode() == 200  # 200 means "URL not found"
    except (error.SSLError, urllib.error.URLError):
        return True


class Reader(unittest.TestCase):
    """Check that external queries work."""

    @mock.patch("code_include.source_code._get_app_inventory")
    def _test_import(self, content, expected, _get_app_inventory):
        """A generic test function. It tests for some source code from an importable Python object.

        Args:
            content (list[str]):
                The lines that the user provides in a standard code-include block.
            expected (str):
                The converted source-code text that will be tested for.
            _get_app_inventory (:class:`mock.mock.MagicMock`):
                The function that's normally used to query a Sphinx
                project's inventory to find every HTML file-path and
                tag-able header.

        """
        _get_app_inventory.return_value = {"non-empty": {"information": tuple()}}
        directive = common.make_mock_directive(content)
        nodes = directive.run()

        self.assertNotEqual([], nodes)
        self.assertEqual(1, len(nodes))
        self.assertEqual(expected, nodes[0].astext())

    # TODO : Add skip if the URL isn't readable
    @mock.patch("code_include.source_code._get_source_module_data")
    @mock.patch("code_include.source_code._get_source_code_from_object")
    @mock.patch("code_include.source_code._get_app_inventory")
    @unittest.skipIf(
        _skip_from_ssl_error("https://ways.readthedocs.io/en/latest/objects.inv"),
        "URL could not be reached",
    )
    def test_url(
        self, _get_app_inventory, _get_source_code_from_object, _get_source_module_data
    ):
        """Get the source-code of some project from a URL.

        Args:
            _get_app_inventory (:class:`mock.mock.MagicMock`):
                The function that's normally used to query a Sphinx
                project's inventory to find every HTML file-path and
                tag-able header.
            _get_source_code_from_object (:class:`mock.mock.MagicMock`):
                Force this function to get the code from intersphinx.
            _get_source_module_data (:class:`mock.mock.MagicMock`):
                A function that is mocked so that we can skip some of
                the less important tag-parsing functions and get to the
                point of this function - testing generated source-code.

        """
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

    def test_import(self):
        """Get the source-code of an importable object."""
        version = sys.version_info

        if version.major < 3:
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
        elif version.major >= 3 and version.minor <= 5:
            expected = textwrap.dedent(
                '''\
                def join(a, *p):
                    """Join two or more pathname components, inserting '/' as needed.
                    If any component is an absolute path, all previous path components
                    will be discarded.  An empty last part will result in a path that
                    ends with a separator."""
                    sep = _get_sep(a)
                    path = a
                    try:
                        if not p:
                            path[:0] + sep  #23780: Ensure compatible data type even if p is null.
                        for b in p:
                            if b.startswith(sep):
                                path = b
                            elif not path or path.endswith(sep):
                                path += b
                            else:
                                path += sep + b
                    except (TypeError, AttributeError, BytesWarning):
                        genericpath._check_arg_types('join', a, *p)
                        raise
                    return path'''
            )
        elif version.major >= 3 and version.minor >= 6:
            expected = textwrap.dedent(
                '''\
                def join(a, *p):
                    """Join two or more pathname components, inserting '/' as needed.
                    If any component is an absolute path, all previous path components
                    will be discarded.  An empty last part will result in a path that
                    ends with a separator."""
                    a = os.fspath(a)
                    sep = _get_sep(a)
                    path = a
                    try:
                        if not p:
                            path[:0] + sep  #23780: Ensure compatible data type even if p is null.
                        for b in map(os.fspath, p):
                            if b.startswith(sep):
                                path = b
                            elif not path or path.endswith(sep):
                                path += b
                            else:
                                path += sep + b
                    except (TypeError, AttributeError, BytesWarning):
                        genericpath._check_arg_types('join', a, *p)
                        raise
                    return path'''
            )
        else:
            raise NotImplementedError(
                'Version "{version}" is not supported.'.format(version=version)
            )

        content = [":func:`os.path.join`"]
        self._test_import(content, expected)  # pylint: disable=no-value-for-parameter

    def test_class(self):
        """Get the source-code of an importable class."""
        content = [":class:`ways.plugin.Plugin`"]
        expected = textwrap.dedent(
            """\
            class Plugin(object):

                '''An add-on that is later retrieved by Context to gather its data.'''

                add_to_registry = True
                _data = dict()

                def __init__(self):
                    '''Create the object and keep a reference to the cache.'''
                    super(Plugin, self).__init__()

                @property
                def data(self):
                    '''dict[str]: The display properties (like {'color': 'red'}).'''
                    return self._data

                @data.setter
                def data(self, value):
                    self._data = value"""
        )

        self._test_import(content, expected)  # pylint: disable=no-value-for-parameter

    def test_function(self):
        """Get the source-code of an importable function."""
        content = [":func:`ways.plugin.get_assignment`"]
        expected = textwrap.dedent(
            """\
            def get_assignment(obj):
                try:
                    return obj.get_assignment()
                except AttributeError:
                    return common.DEFAULT_ASSIGNMENT"""
        )

        self._test_import(content, expected)  # pylint: disable=no-value-for-parameter

    def test_method(self):
        """Get the source-code of an importable method."""
        content = [":meth:`ways.plugin.Plugin.__init__`"]
        expected = textwrap.dedent(
            """\
            def __init__(self):
                '''Create the object and keep a reference to the cache.'''
                super(Plugin, self).__init__()"""
        )

        self._test_import(content, expected)  # pylint: disable=no-value-for-parameter

    def test_module(self):
        """Get the source-code of an importable module."""
        content = [":meth:`ways.plugin`"]
        expected = textwrap.dedent(
            """\
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-

            '''A module that holds Plugin classes - objects that combine into a Context.'''

            # IMPORT STANDARD LIBRARIES
            import uuid

            # IMPORT THIRD-PARTY LIBRARIES
            import ways
            import six

            # IMPORT LOCAL LIBRARIES
            from .core import check
            from . import common
            from . import cache


            class PluginRegistry(type):

                '''A metaclass that adds newly-created Plugin objects to a cache.'''

                def __new__(mcs, clsname, bases, attrs):
                    '''Add the created object to the HistoryCache.'''
                    new_class = super(PluginRegistry, mcs).__new__(
                        mcs, clsname, bases, attrs)

                    # TODO : We still need to not be using 'Plugin' ...
                    # If we explicitly state not to register a plugin, don't register it
                    # If add_to_registry isn't defined for this Plugin,
                    # assume that we should register it
                    #
                    try:
                        if new_class.__name__ == 'Plugin' or not new_class.add_to_registry:
                            return new_class
                    except AttributeError:
                        return new_class

                    assignment = get_assignment(new_class)

                    ways.add_plugin(new_class(), assignment)

                    return new_class


            @six.add_metaclass(PluginRegistry)
            class Plugin(object):

                '''An add-on that is later retrieved by Context to gather its data.'''

                add_to_registry = True
                _data = dict()

                def __init__(self):
                    '''Create the object and keep a reference to the cache.'''
                    super(Plugin, self).__init__()

                @property
                def data(self):
                    '''dict[str]: The display properties (like {'color': 'red'}).'''
                    return self._data

                @data.setter
                def data(self, value):
                    self._data = value


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

                def __init__(self, sources, info, assignment):
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

                    self._info = info
                    self.sources = tuple(sources)
                    self._data = self._info.get('data', dict())
                    self.assignment = assignment

                    super(DataPlugin, self).__init__()

                def _toggle_read_only(self):
                    '''Change the stored data to be overridable or not.'''
                    try:
                        self._info.settable = not self._info.settable
                    except AttributeError:
                        pass

                @classmethod
                def _required_keys(cls):
                    '''tuple[str]: Keys that must be set in our Plugin.'''
                    return ('hierarchy', )

                def is_findable(self):
                    '''If this Plugin is okay to query directly.

                    Some plugins are meant to be combined with other plugins and aren't
                    actually meant to be queried by themselves. This kind of behavior is
                    allowed by our system using the 'findable' key.

                    '''
                    return self._info.get('findable', True)

                def is_hidden(self):
                    '''bool: If this Plugin would be hidden (from view or from code).'''
                    return self._info.get('hidden', False)

                def is_navigatable(self):
                    '''bool: If we're allowed to move into the mapping in this instance.'''
                    return self._info.get('navigatable', True)

                def is_selectable(self):
                    '''bool: If this mapping were displayed - whether it is selectable.'''
                    return self._info.get('selectable', True)

                def get_assignment(self):
                    return self.assignment

                def get_groups(self):
                    '''The groups that this Plugin evaluates onto.

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

                def get_id(self):
                    '''str: The name associated with this Plugin.'''
                    return self._info['id']

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
                    return self._info.get('max_folder', self.get_mapping())

                def get_platforms(self):
                    '''tuple[str]: The platforms that this Plugin is allowed to run on.'''
                    return self._info.get('platforms', ('*', ))

                def get_uses(self):
                    '''tuple[str]: The Context hierarchies this instance depends on.'''
                    return self._info.get('uses', tuple())

                def get_uuid(self):
                    '''str: A unique ID for this plugin.'''
                    return self._info['uuid']

                def __repr__(self):
                    '''str: The information needed to reproduce this instance.'''
                    return '{cls_}(sources={sources!r}, data={data})'.format(
                        cls_=self.__class__.__name__,
                        sources=self.sources,
                        data=dict(self._info))

                    # return '{cls_}(sources={sources!r}, uuid={uid})'.format(
                    #     cls_=self.__class__.__name__,
                    #     sources=self.sources,
                    #     uid=self.get_uuid())

                # def __str__(self):
                #     '''str: A pretty-print of the plugin.'''
                #     return '{cls_}(sources={sources!r}, uuid={uid})'.format(
                #         cls_=self.__class__.__name__,
                #         sources=self.sources,
                #         uid=self.get_uuid())


            def get_assignment(obj):
                try:
                    return obj.get_assignment()
                except AttributeError:
                    return common.DEFAULT_ASSIGNMENT


            if __name__ == '__main__':
                print(__doc__)"""
        )

        self._test_import(content, expected)  # pylint: disable=no-value-for-parameter
