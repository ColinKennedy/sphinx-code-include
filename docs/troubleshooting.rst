===============
Troubleshooting
===============

The code-include is not showing up. What do I do?
=================================================

Add Fallback Text
+++++++++++++++++

If you add ``:fallback-text:`` to your ``code-include`` directive, even if your
target is missing, ``code-include`` will still always show something.

::

    .. code-include :: :func:`foo`


Enable Logging
++++++++++++++

Instead of building your sphinx documentation with a command like

.. code-block:: sh

   sphinx-build documentation/source documentation/build

Try using

.. code-block:: sh

   LOG_LEVEL=0 sphinx-build documentation/source documentation/build

``code-include`` comes with logging messages and ``$LOG_LEVEL`` controls the verbosity.

0 = all+ (show everything)
10 = debug+ (very verbose)
20 = info+ (useful messages)
30 = warning+ (a message indicating a cause for concern)
40 = errors+ (something broke in an unrecoverable way)


Enable Exceptions
+++++++++++++++++

``code-include`` by default doesn't prevent docs from building if an exception is found.
You can disable this (e.g. raise exceptions) by adding this to your ``conf.py``:

.. code-block:: python

    code_include_reraise = True
