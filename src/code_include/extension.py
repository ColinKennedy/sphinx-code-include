#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that adds the code-include directive to Sphinx."""

import logging
import textwrap
import typing

from docutils import nodes
from docutils.parsers import rst
from sphinx import application as application_
from sphinx.writers import html5

from . import error_classes
from . import formatter
from . import source_code

_LOGGER = logging.getLogger(__name__)


class _DocumentationHyperlink(nodes.General, nodes.Element):
    """A container that makes hyperlink text to a Python object's documentation."""


class _SourceCodeHyperlink(nodes.General, nodes.Element):
    """A container that makes hyperlink text to source code."""


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
        "fallback-text": rst.directives.unchanged,
    }

    def _is_link_requested(self) -> bool:
        """bool: Check if the user wants to link to the Python documentation."""
        return "link-to-documentation" in self.options

    def _is_source_requested(self) -> bool:
        """bool: Check if the user wants to link to the original Python source-code."""
        return "link-to-source" in self.options

    def _needs_unindent(self) -> bool:
        """bool: Check if the user doesn't want to unindent the discovered code."""
        return "no-unindent" not in self.options

    @staticmethod
    def _reraise_exception() -> bool:
        """bool: Check if the user wants to force-raise any found exceptions."""
        if not source_code.APPLICATION:
            return False

        return (
            source_code.APPLICATION.config._raw_config.get(  # pylint: disable=protected-access
                "code_include_reraise",
            )
            or False
        )

    def _get_code(
        self,
        directive: str,
        namespace: str,
        prefer_import: bool = True,
    ) -> typing.Optional[source_code.SourceResult]:
        """Get the source code that the user requested.

        Args:
            directive:
                The tag / target that the user expects the namespace to be.
                e.g. "func", "py:class", "class", etc.
            namespace:
                The identifier string that locates this code.
                Example: "some_package_name.module_name.KlassName.get_foo".
            prefer_import:
                If ``False``, look for source code from Sphinx before and if not found,
                do a real Python import for the source code. If ``True`` then do a
                Python import first, instead.

        Returns:
            The found source code, if any.

        """
        try:
            return source_code.get_source_code(
                directive, namespace, prefer_import=prefer_import
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            _LOGGER.warning(
                "code-include failed to find source code. Now trying fallback logic.",
            )
            self._log_exception_context(error, directive, namespace)

            text = self._get_fallback_text()

            if text:
                _LOGGER.info('code-include will use "%s" fallback text.', text)

                return source_code.SourceResult(text, "", "", "")

            if self._reraise_exception():
                raise

        return None

    def _get_fallback_text(self) -> str:
        """str: Some text to render if the Sphinx namespace cannot be found."""
        if "fallback-text" in self.options:
            return typing.cast(str, self.options["fallback-text"])

        return ""

    def _add_documentation_link(
        self,
        result: source_code.SourceResult,
        results: list[nodes.General],
    ) -> None:
        """Add ``result`` as a hyperlink to ``results`` according to user preferences.

        This method adds a link specifically to some Python documentation.

        Args:
            result: The source code description to insert or append.
            results: Blobs of text to render, later.

        """
        hyperlink = _DocumentationHyperlink()
        hyperlink["namespace"] = result.namespace
        hyperlink["href"] = result.documentation_link

        if "link-at-bottom" not in self.options:
            results.insert(0, hyperlink)
        else:
            results.append(hyperlink)

    def _add_source_code_link(
        self,
        result: source_code.SourceResult,
        results: list[nodes.General],
    ) -> None:
        """Add ``result`` as a hyperlink to ``results`` according to user preferences.

        This method adds a link specifically to a namespace's source code,
        assuming it exists. (Intersphinx required).

        Args:
            result: The source code description to insert or append.
            results: Blobs of text to render, later.

        """
        hyperlink = _SourceCodeHyperlink()
        hyperlink["namespace"] = result.namespace
        hyperlink["href"] = result.source_code_link

        if "link-at-bottom" not in self.options:
            results.insert(0, hyperlink)
        else:
            results.append(hyperlink)

    def _log_exception_context(
        self,
        error: Exception,
        directive: str,
        namespace: str,
    ) -> None:
        """Handle exception ``error`` with a useful warning message.

        Args:
            error:
                The Python exception to catch and (we assume) log with a unique message.
            directive:
                The tag / target that the user expects the namespace to be.
                e.g. "func", "py:class", "class", etc.
            namespace:
                The identifier string that locates this code.
                Example: "some_package_name.module_name.KlassName.get_foo".

        """
        if isinstance(error, error_classes.NotFoundFile):
            _LOGGER.warning('File "%s" does not exist.', error)

            return
        if isinstance(error, error_classes.NotFoundUrl):
            _LOGGER.warning('Website "%s" does not exist or is not reachable.', error)

            return
        if isinstance(error, error_classes.MissingTag):
            _LOGGER.warning(
                'Directive "%s" was not found in the intersphinx inventory.',
                directive,
            )

            return
        if isinstance(error, error_classes.MissingNamespace):
            _LOGGER.warning(
                'Namespace "%s" was not found in the intersphinx inventory.',
                namespace,
            )

            return

        if isinstance(error, error_classes.NoMatchFound):
            _LOGGER.warning(
                'Directive / Namespace "%s / %s" has no matching source code.',
                directive,
                namespace,
            )

            return

        _LOGGER.warning(
            'Namespace "%s" has unknown error "%s" class.',
            namespace,
            type(error),
        )

    def run(self) -> list[nodes.literal_block]:
        """Create the code block, if it can.

        Raises:
            :class:`error_classes.MissingContent`:
                If the user forgot to write a target for the code-include directive.

        Returns:
            The code-blocks that this class generates. If any URLs
            are missing, this function warns the user and returns no
            code-blocks, instead.

        """
        _LOGGER.info("code-block directive is now executing.")

        self.assert_has_content()

        target = self.content[0]

        if not target:
            message = "No target for code-include. Directive is missing"

            if self._reraise_exception():
                raise error_classes.MissingContent(message)

            _LOGGER.error(message)

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

        _LOGGER.debug('directive="%s"', directive)
        _LOGGER.debug('namespace="%s"', namespace)
        _LOGGER.debug('is_source_requested="%s"', is_source_requested)
        _LOGGER.debug('is_link_requested="%s"', is_link_requested)

        try:
            result = self._get_code(
                directive,
                namespace,
                prefer_import=not is_source_requested or not is_link_requested,
            )
        except known_exceptions:
            if self._reraise_exception():
                raise

            _LOGGER.warning('"Get Code" logic failed. Returning nothing')

            return []

        if not result:
            _LOGGER.warning(
                'No source code was found for directive / namespace "%s / %s".',
                directive,
                namespace,
            )

            return []

        if self._needs_unindent():
            _LOGGER.debug('Unindenting "%s" namespace code.', result.namespace)

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
            _LOGGER.debug("Adding documentation link to code-include.")

            self._add_documentation_link(result, results)

        if result.source_code_link and is_source_requested:
            _LOGGER.debug("Adding source link to code-include.")

            self._add_source_code_link(result, results)

        _LOGGER.debug('Returning "%s" results', repr(results))

        return results


def setup(application: application_.Sphinx) -> dict[str, bool]:
    """Add the code-include directive to Sphinx.

    Important:
        This function assumes that :func:`sphinx.ext.viewcode.setup` and
        :func:`sphinx.ext.interspinx.setup` both ran before calling this
        function.

    Args:
        application:
            The main class that code-include will register into.

    Returns:
        Configuration settings about this extension.

    """

    def before_documentation(self: html5.HTML5Translator, node: str) -> None:
        """Create a hyperlink with the given node."""
        self.body.append(
            textwrap.dedent(
                """\
            <div style="text-align: right">
                Documentation:
                <a href="{node[href]}">{node[namespace]}</a>
            </div>
            """.format(
                    node=node
                )
            )
        )

    def before_source_code(self: html5.HTML5Translator, node: str) -> None:
        """Create a hyperlink with the given node."""
        self.body.append(
            textwrap.dedent(
                """\
            <div style="text-align: right">
                Source code:
                <a href="{node[href]}">{node[namespace]}</a>
            </div>
            """.format(
                    node=node
                )
            )
        )

    def after(
        self: html5.HTML5Translator, node: typing.Any  # pylint: disable=unused-argument
    ) -> None:
        """Do nothing on-exit."""

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
