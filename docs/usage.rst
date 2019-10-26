=====
Usage
=====

Configuration
=============

To use Sphinx Code Include in a project

- Create a Sphinx project if you haven't already (using ``sphinx-quickstart`` or otherwise)
- Add ``sphinx-code-include`` to your conf.py


.. code-block :: python

    extensions = [
        "code_include.extension",
    ]


Options
=======

This block shows every option that you can add into a ``code-include`` block.

::

    .. code-include :: :func:`module_name.foo`
        :language: python
        :link-at-bottom:
        :link-to-documentation:
        :link-to-source:
        :no-unindent:

Here's a description of what each option does.

 ======================= ==============================================================================================================================
         Option                                                                   Description
 ======================= ==============================================================================================================================
  language                The syntax highlight that will be used. Examples of valid input in `pygment's documentation`_. The default value is "python"
  link-at-bottom          Add source code and/or documentation links at the bottom of the block.
  link-to-documentation   Add a clickable link to where the source code's API documentation is.
  link-to-source          Add a clickable link to where the source code is from.
  no-unindent             If the found source-code has indentation, don't remove any of it.
 ======================= ==============================================================================================================================


Advanced Usage
==============

If you have to use ``link-to-source``, 2 things are required.

- Your project `must be set up for intersphinx`_.
- The project that you're trying to reference must have
  ``sphinx.ext.viewcode`` included in their extensions.


Example Project
===============

``sphinx-code-include`` shows how to use the ``code-include`` directive
in its own documentation.

This page includes this in its text:

::

    .. code-include :: :mod:`conf`


And this is the conf.py that generates this documentation.

.. code-include :: :mod:`conf`


Notice ``intersphinx_mapping`` towards the bottom. This attribute must
be set up to point to your other project. ``intersphinx_mapping`` cannot
be empty. In our case, we'll point it to some external Sphinx project.

::

    .. code-include :: :func:`requests.get`

And this is what the block above renders as:

.. code-include :: :func:`requests.get`

Notice that `requests.get`_ is actually using a different theme than
this documentation's theme but it still renders with the correct color
scheme.

And of course, you can refer to objects in your current project using
``code-include``, too.

::

    .. code-include :: :func:`code_include.helper.memoize`

.. code-include :: :func:`code_include.helper.memoize`


Advanced Customization - Pre-Processor Function
===============================================

You have total control over how source-code is rendered in your Sphinx
project. Say, for example, you want to get source-code of a function but
you want to remove the function's docstring, or delete its comments.

.. note ::

    code_include_preprocessor is only run if your code comes from
    another Sphinx project. If the source-code that you're targetting
    comes from imported content then the pre-processor is ignored.


Add a function called ``code_include_preprocessor`` to your conf.py

.. code-block :: python

    def code_include_preprocessor(soup):
        """`soup` is a :class:`bs4.element.Tag` object."""
        pass

``code-include`` brings in the source-code from projects as HTML tags.
This function lets you directly access and modify those tags before it
gets converted into raw text. So you're free to change whatever you
want and it will be applied to every code-include directive.


.. _must be set up for intersphinx: http://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

.. _pygment's documentation: http://pygments.org/docs/lexers

.. _requests.get: https://requests.kennethreitz.org/en/latest/_modules/requests/api/#get
