#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of tests that access content outside of this repository."""

import unittest

class Reader(unittest.TestCase):
    """Check that external queries work."""

    def test_url(self):
        """Get the source-code of some project from a URL."""
        raise ValueError()
