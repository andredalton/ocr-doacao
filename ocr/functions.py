#!/usr/bin/python
# -*- coding: UTF8 -*-

from __future__ import print_function

from config import DAEMON

import sys
import socket
import hashlib


def port():
    try:
        return int(file_get_contents(DAEMON))
    except (IOError, ValueError):
        return 0


def file_get_contents(fname):
    with open(fname, 'r') as content_file:
        return content_file.read()


def file_write_contents(fname, content):
    fd = open(fname, "w")
    fd.write(content)
    fd.close()


def make_md5(fname, fextension):
    content = file_get_contents(fname+fextension)
    md5 = hashlib.md5(content).hexdigest()
    file_write_contents(fname+".md5", md5)
    return md5


def free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    p = sock.getsockname()[1]
    sock.close()
    return p


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)