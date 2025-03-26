#!/usr/bin/python3
#
# Very simple command line to demonstrate loading 
# a FakeJPEG object from a file and using it to
# generate a fake JPEG using that object.
#
# The pickle file is named on the command line
# and the JPEG is sent to stdout.

import sys
import pickle
import time
from fakejpeg import FakeJPEG

with open(sys.argv[1], "rb") as f:
    fjpeg = pickle.load(f)

# Once you've loaded the FakeJPEG object, you can
# call its generate() method to generate JPEGs
# as many times as you like.

# Simple benchmark, then generate a JPEG to stdout.
benchmark_seconds = 5
print(f"Benchmarking for {benchmark_seconds} seconds", file=sys.stderr)
start = time.time()
jpegs = 0
size = 0
while time.time() < start + benchmark_seconds:
    jpeg = fjpeg.generate()
    size += len(jpeg)
    jpegs += 1
end = time.time()

print(f"Average JPEG generation time: {1000*(end-start)/jpegs:.3f} ms", file=sys.stderr)
print(f"Average generation bandwidth: {size/(end-start)/1024/1024:.1f} MBytes/second", file=sys.stderr)

sys.stdout.buffer.write(fjpeg.generate())
