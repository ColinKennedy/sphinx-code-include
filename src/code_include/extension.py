#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module that adds the code-include directive to Sphinx."""

from docutils import frontend
from docutils import nodes
from docutils.parsers import rst

from . import error_classes
from . import formatter
from . import source_code

_SETTINGS = frontend.OptionParser().get_default_values()


class Directive(rst.Directive):
    """A basic class that creates the syntax-highlighted code.

    Attributes:
        has_content (bool):
            This tells Sphinx to always expect some text on the same line as the directive.
        option_spec (dict[str, callable]):
            A schema which is used to search for optional flags for this directive.

    """

    has_content = True
    option_spec = {
        "no-unindent": rst.directives.flag,
        "language": rst.directives.unchanged,
    }

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

    def _get_code(self, directive, namespace):
        """Get the source code that the user requested.

        Args:
            directive (str):
                The tag / target that the user expects the namespace to be.
                e.g. "func", "py:class", "class", etc.
            namespace (str):
                The identifier string that can be used to locate this code.
                e.g. "some_package_name.module_name.KlassName.get_foo".

        Returns:
            str:
                The found source code.

        """
        try:
            return source_code.get_source_code(directive, namespace)
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
        except error_classes.MissingDirective:
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
                The code-blocks that were generated by this class. If
                any URLs are missing, this function warngs the user and
                returns no code-blocks, instead.

        """
        self.assert_has_content()

        target = self.content[0]

        if not target:
            message = "No target for code-include directive was found"
            self.error(message)

            if self._reraise_exception():
                raise error_classes.MissingContent(message)

            return []

        directive, namespace = formatter.get_raw_content(target)
        directive = formatter.get_converted_directive(directive) or directive

        known_exceptions = (
            error_classes.MissingDirective,
            error_classes.MissingNamespace,
            error_classes.NotFoundFile,
            error_classes.NotFoundUrl,
        )

        try:
            code = self._get_code(directive, namespace)
        except known_exceptions:
            if self._reraise_exception():
                raise

            return []

        if self._needs_unindent():
            code = formatter.unindent_outer_whitespace(code)

        node = nodes.literal_block(code, code)
        node["language"] = self.options.get("language", "python")

        self.add_name(node)

        return [node]


def setup(application):
    """Add the code-include directive to Sphinx.

    Important:
        This function assumes that :func:`sphinx.ext.viewcode.setup` and
        :func:`sphinx.ext.interspinx.setup` have both been run before
        this function is called.

    Args:
        application (:class:`sphinx.application.Sphinx`):
            The main class which code-include is registered into.

    Returns:
        dict[str, bool]: Configuration settings about this extension.

    """
    source_code.APPLICATION = application

    application.add_directive("code-include", Directive)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
