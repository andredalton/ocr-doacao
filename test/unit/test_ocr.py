#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock

import sys
import os
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", ".."))
from ocr.ocr import call_tesseract


class TestOcr(unittest.TestCase):
    @mock.patch('ocr.ocr.call')
    @mock.patch('ocr.ocr.file_get_contents')
    def test_call_tesseract(self, mock_get, mock_call):
        call_tesseract("anyFile", ".ext")
        mock_call.assert_called_with(['tesseract', '-l', 'por', 'anyFile.ext', 'anyFile'])
        mock_get.assert_called_with("anyFile.txt")

if __name__ == '__main__':
    unittest.main()