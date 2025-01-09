========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |dependabot|
        | |codecov|
        | |codacy|
    * - package
      - | |version| |wheel| |oses| |supported-versions| |supported-implementations|
        | |commits-since|


.. |dependabot| image:: https://img.shields.io/badge/dependabot-025E8C?style=for-the-badge&logo=dependabot&logoColor=white
    :target: https://img.shields.io/badge/dependabot-025E8C?style=for-the-badge&logo=dependabot&logoColor=white
    :alt: Dependencies Auto-Checks are enabled

.. |docs| image:: https://readthedocs.org/projects/sphinx-code-include/badge/?style=flat
    :target: https://readthedocs.org/projects/sphinx-code-include
    :alt: Documentation Status

.. |codecov| image:: https://codecov.io/github/ColinKennedy/sphinx-code-include/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ColinKennedy/sphinx-code-include

.. |codacy| image:: https://app.codacy.com/project/badge/Grade/0ea5a564f6fe4f79bd956863943add4b
    :target: https://app.codacy.com/gh/ColinKennedy/sphinx-code-include/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
    :alt: Codacy Code Quality Status

.. |oses| image:: https://img.shields.io/badge/os-linux%20%7C%20macOS%20%7C%20windows-blue
    :alt: Supported OSes
    :target: https://img.shields.io/badge/os-linux%20%7C%20macOS%20%7C%20windows-blue

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

.. |commits-since| image:: https://img.shields.io/github/commits-since/ColinKennedy/sphinx-code-include/v2.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ColinKennedy/sphinx-code-include/compare/v2.0.0...master



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
