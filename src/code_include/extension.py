#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that adds the code-include directive to Sphinx."""

import textwrap

from docutils import frontend
from docutils import nodes
from docutils.parsers import rst

from . import error_classes
from . import formatter
from . import source_code

_SETTINGS = frontend.OptionParser().get_default_values()


class _DocumentationHyperlink(nodes.General, nodes.Element):
    """A container that makes hyperlink text to a Python object's documentation."""

    pass


class _SourceCodeHyperlink(nodes.General, nodes.Element):
    """A container that makes hyperlink text to source code."""

    pass


class Directive(rst.Directive):
    """A basic class that creates the syntax-highlighted code.

    Attributes:
        has_content (bool):
            This tells Sphinx to always expect some text on the same line as the directive.
        option_spec (dict[str, callable]):
            A schema searches for optional flags for this directive.

    """

    has_content = True
    option_spec = {
        "language": rst.directives.unchanged,
        "link-at-bottom": rst.directives.flag,
        "link-to-documentation": rst.directives.flag,
        "link-to-source": rst.directives.flag,
        "no-unindent": rst.directives.flag,
    }

    def _is_link_requested(self):
        """bool: Check if the user wants to link to the Python documentation."""
        return "link-to-documentation" in self.options

    def _is_source_requested(self):
        """bool: Check if the user wants to link to the original Python source-code."""
        return "link-to-source" in self.options

    def _needs_unindent(self):
        """bool: Check if the user doesn't want to unindent the discovered code."""
        return "no-unindent" not in self.options

    @staticmethod
    def _reraise_exception():
        """bool: Check if the user wants to force-raise any found exceptions."""
        if not source_code.APPLICATION:
            return False

        return (
            hasattr(source_code.APPLICATION.config, "code_include_reraise")
            and source_code.APPLICATION.config.code_include_reraise
        )

    def _get_code(self, directive, namespace, prefer_import=True):
        """Get the source code that the user requested.

        Args:
            directive (str):
                The tag / target that the user expects the namespace to be.
                e.g. "func", "py:class", "class", etc.
            namespace (str):
                The identifier string that locates this code.
                Example: "some_package_name.module_name.KlassName.get_foo".

        Returns:
            str:
                The found source code.

        """
        try:
            return source_code.get_source_code(directive, namespace, prefer_import=prefer_import)
        except error_classes.NotFoundFile as error:
            self.warning('File "{error}" does not exist.'.format(error=error))

            raise
        except error_classes.NotFoundUrl as error:
            self.warning(
                'Website "{error}" does not exist or is not reachable.'.format(
                    error=error
                )
            )

            raise
        except error_classes.MissingTag:
            self.warning(
                'Directive "{directive}" was not found in the intersphinx inventory.'.format(
                    directive=directive
                )
            )

            raise
        except error_classes.MissingNamespace:
            self.warning(
                'Namespace "{namespace}" was not found in the intersphinx inventory.'.format(
                    namespace=namespace
                )
            )

            raise

    def run(self):
        """Create the code block, if it can.

        Raises:
            :class:`error_classes.MissingContent`:
                If the user forgot to write a target for the code-include directive.

        Returns:
            list[:class:`docutils.nodes.literal_block`]:
                The code-blocks that this class generates. If any URLs
                are missing, this function warns the user and returns no
                code-blocks, instead.

        """
        self.assert_has_content()

        target = self.content[0]

        if not target:
            message = "No target for code-include directive is missing"
            self.error(message)

            if self._reraise_exception():
                raise error_classes.MissingContent(message)

            return []

        directive, namespace = formatter.get_raw_content(target)
        directive = formatter.get_converted_directive(directive) or directive

        known_exceptions = (
            error_classes.MissingTag,
            error_classes.MissingNamespace,
            error_classes.NotFoundFile,
            error_classes.NotFoundUrl,
        )

        is_source_requested = self._is_source_requested()
        is_link_requested = self._is_link_requested()

        try:
            result = self._get_code(
                directive,
                namespace,
                prefer_import=not is_source_requested or not is_link_requested,
            )
        except known_exceptions:
            if self._reraise_exception():
                raise

            return []

        if self._needs_unindent():
            result = result.__class__(
                formatter.unindent_outer_whitespace(result.code),
                result.namespace,
                result.source_code_link,
                result.documentation_link,
            )

        node = nodes.literal_block(result.code, result.code)
        node["language"] = self.options.get("language", "python")

        self.add_name(node)

        results = [node]

        if result.documentation_link and is_link_requested:
            hyperlink = _DocumentationHyperlink()
            hyperlink["namespace"] = result.namespace
            hyperlink["href"] = result.documentation_link

            if "link-at-bottom" not in self.options:
                results.insert(0, hyperlink)
            else:
                results.append(hyperlink)

        if result.source_code_link and is_source_requested:
            hyperlink = _SourceCodeHyperlink()
            hyperlink["namespace"] = result.namespace
            hyperlink["href"] = result.source_code_link

            if "link-at-bottom" not in self.options:
                results.insert(0, hyperlink)
            else:
                results.append(hyperlink)

        return results


def setup(application):
    """Add the code-include directive to Sphinx.

    Important:
        This function assumes that :func:`sphinx.ext.viewcode.setup` and
        :func:`sphinx.ext.interspinx.setup` both ran before calling this
        function.

    Args:
        application (:class:`sphinx.application.Sphinx`):
            The main class that code-include will register into.

    Returns:
        dict[str, bool]: Configuration settings about this extension.

    """
    def before_documentation(self, node):
        """Create a hyperlink with the given node."""
        self.body.append(textwrap.dedent(
            '''\
            <div style="text-align: right">
                Documentation:
                <a href="{node[href]}">{node[namespace]}</a>
            </div>
            '''.format(node=node)))

    def before_source_code(self, node):
        """Create a hyperlink with the given node."""
        self.body.append(textwrap.dedent(
            '''\
            <div style="text-align: right">
                Source code:
                <a href="{node[href]}">{node[namespace]}</a>
            </div>
            '''.format(node=node)))

    def after(self, node):  # pylint: disable=unused-argument
        """Do nothing on-exit."""
        pass

    source_code.APPLICATION = application

    application.add_node(
        _DocumentationHyperlink,
        html=(before_documentation, after),
    )

    application.add_node(
        _SourceCodeHyperlink,
        html=(before_source_code, after),
    )

    application.add_directive(
        "code-include",
        Directive,
    )

    return {"parallel_read_safe": True, "parallel_write_safe": True}
