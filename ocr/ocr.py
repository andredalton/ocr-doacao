#!/usr/bin/python
# -*- coding: UTF8 -*-

from subprocess import call

from .functions import file_get_contents


def call_tesseract(filename, ext):
    call(["tesseract", "-l", "por", filename + ext, filename])
    return file_get_contents(filename + ".txt")