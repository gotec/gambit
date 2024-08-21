"""
An Open Source name disambiguation tool for version control systems.
"""

__author__ = "Christoph Gote"
__email__ = "cgote@ethz.ch"
__version__ = get_distribution('gambit-disambig').version

from .main import disambiguate_aliases  # noqa
