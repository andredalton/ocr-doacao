#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock

import sys
import os
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", ".."))
from ocr.functions import file_get_contents, file_write_contents, free_port, make_md5, port
from ocr.config import DAEMON

class TestFunctions(unittest.TestCase):
    @mock.patch("__builtin__.open")
    def test_file_get_contents(self, mock_open):
        file_get_contents("anyFile")
        mock_open.assert_called_with("anyFile", "r")
        mock_open.side_effect = IOError()
        with self.assertRaises(IOError):
            file_get_contents("anyFile")

    @mock.patch("__builtin__.open")
    def test_file_write_contents(self, mock_open):
        mock_file = mock.Mock()
        mock_file.write.return_value = None
        mock_file.close.return_value = None
        mock_open.return_value = mock_file
        content = "content"
        file_write_contents("anyFile", content)
        mock_open.assert_called_with("anyFile", "w")
        mock_file.write.assert_called_with(content)
        mock_file.close.assert_called_with()

    @mock.patch('ocr.functions.socket')
    def test_free_port(self, mock_socket):
        mock_sock = mock.Mock()
        mock_sock.bind.return_value = None
        mock_sock.close.return_value = None
        mock_sock.getsockname.return_value = ('127.0.0.1', 666)
        mock_socket.socket.return_value = mock_sock

        r = free_port()

        mock_sock.bind.assert_called_with(('localhost', 0))
        mock_sock.getsockname.assert_called_with()
        mock_sock.close.assert_called_with()
        self.assertEqual(r, 666)

    @mock.patch("ocr.functions.file_get_contents")
    def test_port(self, mock_file):
        mock_file.return_value = "666"
        r = port()
        mock_file.assert_called_with(DAEMON)
        self.assertEqual(r, 666)
        mock_file.side_effect = IOError()
        r = port()
        self.assertEqual(r, 0)
        mock_file.side_effect = ValueError()
        r = port()
        self.assertEqual(r, 0)

    @mock.patch("ocr.functions.file_get_contents")
    @mock.patch("ocr.functions.file_write_contents")
    def test_make_md5(self, mock_write, mock_open):
        mock_open.return_value = "anyString"
        r = make_md5("anyFile", ".ext")
        g = "f26de8fe6ef3ede1eca6f261781c4431"
        mock_open.assert_called_with("anyFile.ext")
        mock_write.assert_called_with('anyFile.md5', 'f26de8fe6ef3ede1eca6f261781c4431')
        self.assertEqual(r, g)

if __name__ == '__main__':
    unittest.main()