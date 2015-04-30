#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock

import sys
import os
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", ".."))
from ocr.functions import file_get_contents, free_port, make_md5, port


class TestFunctions(unittest.TestCase):
    @mock.patch("__builtin__.open")
    def test_file_get_contents(self, mock_open):
        file_get_contents("anyFile")
        mock_open.assert_called_with("anyFile", "r")

if __name__ == '__main__':
    unittest.main()