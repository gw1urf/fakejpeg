#!/usr/bin/python3
#
# Generate fake jpeg files. Let's poison some more LLM crawlers!

import os, sys, pickle, random, struct, hashlib
from io import BytesIO
from flask import Flask, send_file

home = os.path.dirname(os.path.realpath(__file__))
sys.path.append(home)

from fakejpeg import FakeJPEG

class JpegSpigot(Flask):
    def __init__(self, template_file):
        with open(template_file, "rb") as pf:
            self.fjpeg = pickle.load(pf)

        if not isinstance(self.fjpeg, FakeJPEG):
            raise Exception("Bad template")

        # Start the Flask application.
        super().__init__("server")

        # Register URL paths.
        self.add_url_rule("/<path:location>", view_func=self.pic_router, methods=["GET"])
        self.add_url_rule("/", view_func=self.top_router, methods=["GET"])

    def top_router(self):
        return self.pic_router("/")

    def pic_router(self, location):
        random.seed(struct.unpack("L", hashlib.md5(location.encode("utf-8")).digest()[:8])[0])
        return send_file(BytesIO(self.fjpeg.generate()), mimetype="image/jpeg")

application = JpegSpigot(f"{home}/jpeg_templates.pkl")

