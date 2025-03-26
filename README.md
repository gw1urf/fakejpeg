# What is it?

This Python class is a simple proof of concept for generating
"fake" JPEGs quickly. You "train" it with a collection of existing
JPEGs and, once trained, you can use it to generate an arbitrary
number of things that seem like JPEGs.

This is part of my attempt to safeguard my web server from aggressive
web crawlers. It's designed to run very quickly, so that it can feed
fake JPEGs to those crawlers on the fly. 

The fake JPEGs do not contain valid compressed data, since generating a
valid compressed stream from generated pixel data would be slow.
Instead, wherever compressed pixel data is required, the generated files
contain random bytes. The result is something that, structurally, appears to
be a valid JPEG and for which most JPEG decoders will generate an actual
image. Most decoders will report warnings about bad Huffman codes, since the
data is *not* correctly structured.

Every web browser I've tried has silently accepted the resulting data and
rendered an image.

The general idea is to have a simple Flask application which can provide an
infinite supply of images on demand, without placing much load on your web
server. On my web server, the class can generate over 500 1280x1024
JPEGs per second.

I'm not going to give too much detail in how to use this code, at this
point. If you're not fairly familiar with deploying web applications and
managing web server load, you probably don't want to be playing with this!

# What do I need?

* Python and Flask. On Debian, ```apt-get install python3-flask``` should
  get you all you need.
* A working web server with the ability to run Python WSGI applications.
  For example, Apache with mod_wsgi.

# Example Flask application

The file, ```index.wsgi``` is an example implementation of a page
which, when correctly set up, will generate pictures on demand. The
script expects to find a file named "jpeg_templates.pkl" containing
a pre-trained FakeJPEG image. I'm supplying an example pickle file,
generated using the "make_templates.py" script from this repo.

To use this script, you'd want something like the following in your Apache config.

    WSGIDaemonProcess fakejpeg threads=10 maximum-requests=10000 user=fakejpeg-user group=fakejpeg-group
    WSGIScriptAlias /fakejpeg-example /path/to/fakejpeg/index.wsgi process-group=fakejpeg application-group=%{GLOBAL}

In the above, ```fakejpeg-user``` and ```fakejpeg-group``` are the username and 
groupname of a user that the application should run as.

Once Apache has been restarted/reconfigured, you should be able to access
any URL under the /fakejpeg-example/ and receive a fake JPEG file back,
which your browser should hopefully render. It'll be a garish mess, but
I hope it'll give those aggressive crawlers something to chew over.
