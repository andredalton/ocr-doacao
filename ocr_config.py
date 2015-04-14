#coding: utf-8

import socket

HOST='/ocr-web'
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tif'])
DAEMON = '.ocr.daemon'
DEBUG = True

def file_get_contents(fname):
    with open(fname, 'r') as content_file:
        return content_file.read()

def free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    p = sock.getsockname()[1]
    sock.close()
    return p

def port():
    try:
        return file_get_contents(DAEMON)
    except (IOError, ValueError):
        return 0
