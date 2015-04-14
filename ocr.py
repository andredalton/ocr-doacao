#coding: utf-8

import os, sys, argparse
from subprocess import call, check_output
from ocr_config import file_get_contents

def call_tesseract(filename):
    call(["tesseract", filename, filename])
    return file_get_contents(filename+".txt")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WebService for OCR.')
    parser.add_argument('-f','--file', metavar='input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input file path')
    parser.add_argument('-o','--out', metavar='output', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='Output file path')
    args = parser.parse_args()

    txt = call_tesseract(os.path.abspath(args.file.name))
    args.out.write(txt)
    args.out.close()
    args.file.close()