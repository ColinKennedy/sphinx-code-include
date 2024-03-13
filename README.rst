========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
        | |codacy|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/sphinx-code-include/badge/?style=flat
    :target: https://readthedocs.org/projects/sphinx-code-include
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/ColinKennedy/sphinx-code-include.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ColinKennedy/sphinx-code-include

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ColinKennedy/sphinx-code-include?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ColinKennedy/sphinx-code-include

.. |requires| image:: https://requires.io/github/ColinKennedy/sphinx-code-include/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ColinKennedy/sphinx-code-include/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/ColinKennedy/sphinx-code-include/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ColinKennedy/sphinx-code-include

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/cd0e702ea8f744088d93c4addd3deeea
    :target: https://www.codacy.com/manual/ColinKennedy/sphinx-code-include?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ColinKennedy/sphinx-code-include&amp;utm_campaign=Badge_Grade
    :alt: Codacy Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/sphinx-code-include.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/sphinx-code-include

.. |wheel| image:: https://img.shields.io/pypi/wheel/sphinx-code-include.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/sphinx-code-include

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/sphinx-code-include.svg
    :alt: Supported versions
    :target: https://pypi.org/project/sphinx-code-include

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/sphinx-code-include.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/sphinx-code-include

.. |commits-since| image:: https://img.shields.io/github/commits-since/ColinKennedy/sphinx-code-include/v1.2.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ColinKennedy/sphinx-code-include/compare/v1.2.0...master



.. end-badges

sphinx-code-include is an extension for Sphinx that lets you render
source-code of any class or function directly into your Sphinx
documentation using only as string.

* Free software: BSD 2-Clause License

Example

::

    .. code-include :: :func:`os.path.join`

This code-include block renders as: (theme is sphinx_rtd_theme)

.. image :: https://user-images.githubusercontent.com/10103049/67256848-f7422380-f43d-11e9-857a-434ba7bf579f.jpg

As long as the string you've chosen is either

- is importable
- is coming from a project that has `sphinx.ext.viewcode`_ enabled

then code-include can find it and render it in your documentation.

Installation
============

::

    pip install sphinx-code-include

You can also install the in-development version with::

    pip install https://github.com/ColinKennedy/sphinx-code-include/archive/master.zip


Documentation
=============


https://sphinx-code-include.readthedocs.io/


Development
===========

To run the all tests run::

    tox

.. _sphinx.ext.viewcode: https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
