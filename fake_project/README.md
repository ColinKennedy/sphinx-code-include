What Is This Project Used For?
==============================

`sphinx-code-include` supports targetting objects in other projects. This
project is used to test that intersphinx support works correctly.


How To Build
============

```bash
PYTHONPATH=$PWD:python:$PYTHONPATH sphinx-build documentation/source documentation/build
```


Add To Unittests
================

Once the documentation is built, copy it to `sphinx-code-include` with this command:

```bash
rm -rf ../tests/fake_project && cp -r documentation/build ../tests/fake_project
```
