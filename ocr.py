#!/usr/bin/python
# -*- coding: UTF8 -*-

import os
import sys

from ocr.ocr import call_tesseract

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WebService for OCR.')
    parser.add_argument('-f', '--file', metavar='input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='Input file path')
    parser.add_argument('-o', '--out', metavar='output', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help='Output file path')
    args = parser.parse_args()

    (fname, fext) = os.path.splitext(os.path.abspath(args.file.name))

    txt = call_tesseract(fname, fext)
    args.out.write(txt)
    args.out.close()
    args.file.close()