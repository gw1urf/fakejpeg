#!/usr/bin/python3
#
# Script which builds some examples into the "images"
# directory.

import pickle
from fakejpeg import FakeJPEG

with open("jpeg_templates.pkl", "rb") as f:
    fake = pickle.load(f)

# Once you've loaded the FakeJPEG object, you can
# call its generate() method to generate JPEGs
# as many times as you like.

for pic in range(10):
    with open(f"images/example{pic}.jpg", "wb") as jpegfile:
        jpegfile.write(fake.generate())
