#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for getting the code that this extension displays."""

import collections
import functools
import inspect
import os

import bs4
import six
from six.moves import urllib

from . import error_classes
from . import helper

_OBJ_TAG = "obj"
APPLICATION = None
SourceResult = collections.namedtuple(
    'SourceResult',
    "code namespace source_code_link documentation_link",
)


@helper.memoize
def _get_all_intersphinx_roots():
    """set[str]: Every file path / URL that the user added to intersphinx's inventory."""
    roots = set()

    try:
        mappings = APPLICATION.config.intersphinx_mapping.items()
    except AttributeError:
        raise EnvironmentError("sphinx.ext.intersphinx was not configured properly.")

    for key, value in mappings:
        if not isinstance(value, six.string_types):
            roots.add(list(value)[0])
        else:
            roots.add(key)

    return roots


def _get_app_inventory():
    """dict[str, dict[str, tuple[str, str, str, str]]]: Get all cached targets + namespaces."""
    if not APPLICATION:
        raise EnvironmentError("code_include did not initialize properly.")

    try:
        return APPLICATION.builder.env.intersphinx_inventory
    except AttributeError:
        raise EnvironmentError("sphinx.ext.intersphinx was not configured properly.")


def _get_module_tag(namespace, directive):
    """Get the project-relative path to some Python class, method, or function.

    Args:
        namespace (str):
            The importable Python location of some class, method, or function.
            Example: "foo.bar.ClassName.get_method_data".
        directive (str):
            The Python type that `namespace` is. Example: "py:method".

    Raises:
        EnvironmentError:
            If `directive` and `namespace` were both found properly but,
            for some reason, the top-level website / file path for the
            Sphinx project stored by intersphinx could not be found.

    Returns:
        tuple[str, str]:
            The exact path, relative to a Sphinx project's root
            directory, where this module is tagged, followed by a tag
            like "foo" which will be later used to get a permalink to
            some header in the HTML file.

    """
    tokens = namespace.split(".")

    if directive in {"py:method"}:
        base = "/".join(tokens[:-2])

        return "_modules/{base}.html".format(base=base), ".".join(tokens[-2:])

    base = "/".join(tokens[:-1])

    return "_modules/{base}.html".format(base=base), tokens[-1]


def _get_page_preprocessor():
    """Find an optional function that will be run on the found source-code tag.

    This function is great way to filter out or add content to
    the returned source-code. For example, if the user wants to
    decompose extra tags from the HTML page, they can define their own
    preprocessor function in conf.py.

    Example:
        Remove all hyper-linked text.

        >>> def code_include_preprocessor(soup):
        >>>     for tag in soup.find_all('a'):
        >>>         tag.decompose()

    Returns:
        callable[:class:`bs4.element.Tag`]:
            The node that will be shown to the user.

    """
    def do_nothing(application):  # pylint: disable=missing-docstring,unused-argument
        pass

    if not APPLICATION:
        return do_nothing

    if "code_include_preprocessor" in APPLICATION.config:
        return APPLICATION.config.code_include_preprocessor

    return do_nothing


def _get_project_url_root(uri, roots):
    """Find the top-level project for some URL / file-path.

    Note:
        The matching `uri` must match an item `roots` exactly.

    Args:
        uri (str):
            The URL / file-path that presumably came from an intersphinx inventory
            file. This path is inside some Sphinx project (which we will find the root of).
        roots (iter[str]):
            Potential file paths / URLs that `uri` is a child of.

    Returns:
        str: The found root. If no root was found, return an empty string.

    """
    for root in roots:
        if uri.startswith(root):
            return root

    return ""


def _get_source_code(uri, tag):
    """Find the exact code for some class, method, attribute, or function.

    Args:
        uri (str):
            The URL / file-path to a HTML file that has Python
            source-code. is function scrapes the HTML file and returns
            the found source-code.
        tag (str):
            The class, method, attribute, or function that will be
            extracted from `uri`.

    Raises:
        :class:`.NotFoundFile`:
            If `uri` is a path to an HTML file but the file does not exist.
        :class:`.NotFoundUrl`:
            If `uri` is a URL and it could not be read properly.

    Returns:
        str:
            The found source-code. This text is returned as raw text
            (no HTML tags are included).

    """
    if os.path.isabs(uri):
        if not os.path.isfile(uri):
            raise error_classes.NotFoundFile(uri)

        with open(uri, "r") as handler:
            contents = handler.read()
    else:
        try:
            contents = urllib.request.urlopen(uri).read()  # pylint: disable=no-member
        except Exception:
            raise error_classes.NotFoundUrl(uri)

    soup = bs4.BeautifulSoup(contents, "html.parser")

    for div in soup.find_all("a", {"class": "viewcode-back"}):
        div.decompose()

    preprocessor = _get_page_preprocessor()

    if not tag:
        # If the user didn't provide a tag, it means that they are
        # trying to get the full module's source code.
        #
        # The start of the source-code block is always marked using <span class="ch">
        #
        child = soup.find("span", {"class": "ch"})
        node = child.parent
        preprocessor(node)

        return node.getText().lstrip()

    node = soup.find("div", {"id": tag})
    preprocessor(node)

    return node.get_text()


def _get_source_module_data(uri, directive):
    """Find the full path to a HTML file and the tagged content to retrieve.

    Returns:
        tuple[str, str]:
            The absolute path to an HTML file and the "#foo" tag (this
            function returns without the "#") that would normally be
            used as a permalink to some header in the HTML file.

    """
    url, tag = uri.split("#")  # `url` might be a file path or web URL
    available_roots = _get_all_intersphinx_roots()
    root = _get_project_url_root(url, available_roots)

    if not root:
        raise EnvironmentError(
            'URL "{url}" isn\'t in any of the available projects, "{roots}".'.format(
                url=url, roots=sorted(available_roots)
            )
        )

    module_path, tag = _get_module_tag(tag, directive)

    return (root + "/" + module_path, tag)


def _get_source_code_from_inventory(tag, namespace):
    """Get the raw code of some class, method, attribute, or function.

    Args:
        tag (str):
            The Python type that `namespace` is. Example: "py:method".
        namespace (str):
            The importable Python location of some class, method, or function.
            Example: "foo.bar.ClassName.get_method_data".

    Raises:
        RuntimeError:
            If no intersphinx inventory cache could be found.
        :class:`.MissingTag`:
            If `tag` wasn't found in any Sphinx project in the
            intersphinx inventory cache.
        :class:`.MissingNamespace`:
            If `tag` was in the intersphinx inventory cache but
            the no `namespace` could be found in any Sphinx project in
            the intersphinx inventory cache.

    Returns:
        str: The found source-code for `namespace`, with a type of `tag`.

    """
    def __get_uri(tag, cache):
        """Find a URI, relative to the Sphinx project, that points to source code.

        The basic logic of this function goes like this. If `tag`
        is "obj", try every possible type of tag before raising an
        exception. If it isn't "obj" then raise an exception as soon as
        one is needed.

        Args:
            tag (str):
                A type of marker used by Sphinx to find source code.
                Examples: "py:class", "py:staticmethod", "py:function", "obj".
            cache (dict[str, dict[str, tuple[str, str, str, str]]]):
                Get all cached targets + namespaces.

        Returns:
            str:
                The project-relative path.
                Example: "api/fake_project.html#module-fake_project.basic".

        """
        tags = [tag]

        if tag == "obj":
            # If the user doesn't know the tag-type of `namespace` then we must
            # check every possible type, manually.
            #
            tags = [
                "py:attribute",
                "py:function",
                "py:classmethod",
                "py:staticmethod",
                "py:method",
                "py:class",
                "py:module",
            ]

        for tag_ in tags:
            try:
                typed_tag_data = cache[tag_]
            except KeyError:
                if tag != _OBJ_TAG:
                    raise error_classes.MissingTag(
                        'Tag "{tag_}" was invalid. Options were, "{options}".'.format(
                            tag_=tag_, options=sorted(cache)
                        )
                    )

                continue

            try:
                _, _, uri, _ = typed_tag_data[namespace]
            except KeyError:
                if tag != _OBJ_TAG:
                    raise error_classes.MissingNamespace(
                        'Namespace "{namespace}" was invalid. Options were, "{options}".'.format(
                            namespace=namespace, options=sorted(typed_tag_data)
                        )
                    )

                continue

            return uri

        raise error_classes.MissingNamespace(
            'Namespace "{namespace}" cound not be found for any tag searched by :obj:.'.format(
                namespace=namespace
            )
        )

    cache = _get_app_inventory()

    if not cache:
        raise RuntimeError(
            "No application could be found. Cannot render this node. "
            "Did intersphinx have a chance to run?"
        )

    uri = __get_uri(tag, cache)
    module_url, tag = _get_source_module_data(uri, tag)
    code = _get_source_code(module_url, tag)
    full_source_code_url = module_url + "#" + tag

    return SourceResult(code, namespace, full_source_code_url, uri)


def _get_source_code_from_object(namespace):
    """Import a Python namespace path and get source code directly from it.

    Args:
        namespace (str):
            The importable Python location of some class, method, or function.
            Example: "foo.bar.ClassName.get_method_data".

    Returns:
        str: The found source code, assuming `namespace` describes an importable location.

    """
    def _recursively_find_first_importable_object(namespaces):
        """Find the closest Python module to import from.

        If `namespaces` isn't importable, this function will re-try
        using the parent namespace of `namespaces`.

        Args:
            namespaces (list[str]):
                The Python namespace, split into parts.
                e.g. ["foo", "bar", "ClassName", "get_method_data"].

        Returns:
            object or NoneType:
                The found importable object or nothing if `namespaces` isn't importable.

        """
        if not namespaces:
            return None

        try:
            return __import__(".".join(namespaces))
        except ImportError:
            return _recursively_find_first_importable_object(namespaces[:-1])

    def _resolve_object(object_, namespace):
        """Get a Python object located at `namespace`, using a root `object_`.

        Args:
            object_ (object):
                A Python module that contains `namespace`.
                e.g. The `os` module.
            namespace (str):
                A dot-separated string of some attribute, class, or
                function that is located within `object_`.
                e.g. "path.join".

        Returns:
            object: The resolved class, function, attribute, or module.

        """
        if object_.__name__ == namespace:
            return object_

        if not namespace:
            return object_

        root_namespace = object_.__name__ + "."  # Example: `os.`
        tail = namespace[len(root_namespace):]  # Example: `path.join`

        objects = tail.split(".")  # Example: ["path", "join"]
        parent = object_

        for item in objects:
            try:
                parent = getattr(parent, item)
            except AttributeError:
                return None

        return parent

    namespaces = namespace.split(".")
    object_ = _recursively_find_first_importable_object(namespaces)

    if not object_:
        return None

    resolved_object = _resolve_object(object_, namespace)

    if not resolved_object:
        return None

    lines, _ = inspect.getsourcelines(resolved_object)

    return SourceResult("".join(lines), resolved_object, "", "")


def get_source_code(directive, namespace, prefer_import=False):
    """Find the raw source code of some class, method, attribute, or function.

    This function first tries to import the path given by `namespace`
    directly, because that's the most sure-fire way of getting the
    source code. But if it can't be imported, this function will fall
    back to intersphinx's inventory to see if it was loaded as part of
    this Sphinx project.

    Args:
        directive (str):
            The Python type that `namespace` is. Example: "py:method".
        namespace (str):
            The importable Python location of some class, method, or function.
            Example: "foo.bar.ClassName.get_method_data".

    Returns:
        str: The found source code.

    """
    if prefer_import:
        strategy = [
            _get_source_code_from_object,
            functools.partial(_get_source_code_from_inventory, directive),
        ]
    else:
        strategy = [
            functools.partial(_get_source_code_from_inventory, directive),
            _get_source_code_from_object,
        ]

    for getter in strategy:
        code = getter(namespace)

        if code:
            return code

    return None
