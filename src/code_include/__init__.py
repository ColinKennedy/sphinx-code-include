"""The private implementation of ``.. code-include ::`` directive."""

import logging
import os
import sys

_LOGGER = logging.getLogger(__name__)
_HANDLER = logging.StreamHandler(sys.stdout)
_HANDLER.setLevel(logging.DEBUG)
_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_HANDLER.setFormatter(_FORMATTER)
_LOGGER.addHandler(_HANDLER)

_LEVEL = os.getenv("LOG_LEVEL")

if _LEVEL:
    _LOGGER.setLevel(min(0, int(_LEVEL)))
