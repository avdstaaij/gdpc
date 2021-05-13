#! /usr/bin/python3
"""### Test various aspects of the framework automatically.

The tests contained in this file include:

- 

It is not meant to be imported.
"""

__all__ = []
__version__ = "v4.2_dev"

import random

import bitarray
import blockColours
import example
import interfaceUtils
import mapUtils
import visualizeMap
import worldLoader

if __name__ == '__main__':
  TESTS = ()
  
  print(f"Beginning test suite for version {__version__}: {len(TESTS)}")
