"""
An Open Source name disambiguation tool for version control systems.
"""

import importlib.metadata

__author__ = "Christoph Gote"
__email__ = "cgote@ethz.ch"
__version__ = importlib.metadata.version('gambit-disambig')

from .main import disambiguate_aliases  # noqa
