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

.. |codacy| image:: https://img.shields.io/codacy/grade/foo_bar_replace_later.svg
    :target: https://www.codacy.com/app/ColinKennedy/sphinx-code-include
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

.. |commits-since| image:: https://img.shields.io/github/commits-since/ColinKennedy/sphinx-code-include/v1.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ColinKennedy/sphinx-code-include/compare/v1.0.0...master



.. end-badges

Include source code from any Sphinx project using only its import path

* Free software: BSD 2-Clause License

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

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
