#!/usr/bin/python
# -*- coding: UTF8 -*-

from ocr import DAEMON, DEBUG
from ocr.web_service import WebView
import os
import socket


def valid_port(value):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ivalue = int(value)
        result = sock.connect_ex(('127.0.0.1', ivalue))
    except (OverflowError, ValueError):
        sock.close()
        raise argparse.ArgumentTypeError("%s is not a valid port [0-65555]." % value)
    if result == 0:
        sock.close()
        raise argparse.ArgumentTypeError("The port %s is alread in use." % value)
    sock.close()
    return ivalue


def valid_ip(value):
    try:
        socket.inet_aton(value)
    except socket.error:
        raise argparse.ArgumentTypeError("%s is not a valid ip." % value)
    return value

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WebService for OCR.')
    parser.add_argument('-H', '--host', metavar='IP', nargs='?', type=valid_ip, help='Host ip', default='0.0.0.0')
    parser.add_argument('-p', '--port', metavar='PORT', nargs='?', type=valid_port, help='Port number', default=5000)
    args = parser.parse_args()

    if args.port == 0:
        args.port = free_port()

    f = os.open(DAEMON, os.O_WRONLY | os.O_CREAT)
    os.write(f, str(args.port))
    os.close(f)

    web = WebView(debug=DEBUG, port=args.port, host=args.host)
    web.start()

    try:
        os.remove(DAEMON)
    except OSError:
        if DEBUG:
            # Em caso de debug este comando roda duas vezes.
            pass
        else:
            raise OSError