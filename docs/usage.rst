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
        :no-unindent:
        :language: python

Here's a description of what each option does.

 ============= ==============================================================================================================================
    Option                                                              Description
 ============= ==============================================================================================================================
  no-unindent   If the found source-code is nested in another Python object, keep the initial indentation.
  language      The syntax highlight that will be used. Examples of valid input in `pygment's documentation`_. The default value is "python"
 ============= ==============================================================================================================================

.. TODO talk about the preprocessor function
.. TODO Add "link-to-source"
..
.. Option|Description
.. link-to-source|If the found source-code comes from another Sphinx project, link to that project's source-code.
.. no-unindent|If the found source-code is nested in another Python object, keep the initial indentation.
.. language|The syntax highlight that will be used. Examples of valid input in `pygment's documentation`_. The default value is "python"


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
be set up to point to your other project. In our case, we'll point it to
some external Sphinx project.

.. TODO finish this code-include

.. code-include :: :func:`foo.bar`


.. _must be set up for intersphinx: http://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

.. _pygment's documentation: http://pygments.org/docs/lexers
