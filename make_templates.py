#!/usr/bin/python3
#
# Very simple command line for generating a pickle
# containing a pre-initialised FakeJPEG object from
# a list of files on the command line.
#
# The resulting object is pickled and output to 
# stdout.

import sys
import logging
import pickle
from fakejpeg import FakeJPEG

logging.basicConfig(level = logging.DEBUG, format = "%(message)s")

logger = logging.getLogger(sys.argv[0])

fjpeg = FakeJPEG(sys.argv[1:], logger=logger)
pickle.dump(fjpeg, sys.stdout.buffer)
