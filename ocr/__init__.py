#!/usr/bin/python
# -*- coding: UTF8 -*-

from __future__ import print_function

from config import HOST, ALLOWED_EXTENSIONS, DAEMON, DEBUG, ONG_FOLDER, UPLOAD_FOLDER, IMG_NAME, BD_USER, BD_PASSWORD,\
    BD_HOST, BD_NAME

import sys
import socket
import hashlib


def port():
    try:
        return file_get_contents(DAEMON)
    except (IOError, ValueError):
        return 0


def file_get_contents(fname):
    with open(fname, 'r') as content_file:
        return content_file.read()


def make_md5(fname, fextension):
    md5 = hashlib.md5(open(fname+fextension, 'rb').read()).hexdigest()
    fmd5 = open(fname+".md5", "w")
    fmd5.write(md5)
    fmd5.close()
    return md5


def free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    p = sock.getsockname()[1]
    sock.close()
    return p


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)