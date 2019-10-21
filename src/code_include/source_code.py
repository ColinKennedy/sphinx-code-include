#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for getting the code that this extension displays."""

import os

import bs4
import six
from six.moves import urllib

from . import error_classes
from . import helper

APPLICATION = None


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
        return dict()

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
    def do_nothing(application):
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
        # The start of the source-code block is always marked using <span class="ch">
        child = soup.find("span", {"class": "ch"})
        node = child.parent
        preprocessor(node)

        return node.getText().lstrip()
    else:
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


def get_source_code(directive, namespace):
    """Get the raw code of some class, method, attribute, or function.

    Args:
        directive (str):
            The Python type that `namespace` is. Example: "py:method".
        namespace (str):
            The importable Python location of some class, method, or function.
            Example: "foo.bar.ClassName.get_method_data".

    Raises:
        RuntimeError:
            If no intersphinx inventory cache could be found.
        :class:`.MissingDirective`:
            If `directive` wasn't found in any Sphinx project in the
            intersphinx inventory cache.
        :class:`.MissingNamespace`:
            If `directive` was in the intersphinx inventory cache but
            the no `namespace` could be found in any Sphinx project in
            the intersphinx inventory cache.

    Returns:
        str: The found source-code for `namespace`, with a type of `directive`.

    """
    cache = _get_app_inventory()

    if not cache:
        raise RuntimeError(
            "No application could be found. Cannot render this node. "
            "Did intersphinx have a chance to run?"
        )

    try:
        typed_directive_data = cache[directive]
    except KeyError:
        raise error_classes.MissingDirective(
            'Directive "{directive}" was invalid. Options were, "{options}".'.format(
                directive=directive, options=sorted(cache)
            )
        )

    try:
        _, _, uri, _ = typed_directive_data[namespace]
    except KeyError:
        raise error_classes.MissingNamespace(
            'Namespace "{namespace}" was invalid. Options were, "{options}".'.format(
                namespace=namespace, options=sorted(typed_directive_data)
            )
        )

    module_url, tag = _get_source_module_data(uri, directive)

    return _get_source_code(module_url, tag)
