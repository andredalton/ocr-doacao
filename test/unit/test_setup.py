#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock

import sys
import os
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", ".."))
from ocr.setup import is_installed, create_tables, create_database, new_ong_dir
from ocr.config import ONG_FOLDER, BD_NAME


class TestSetup(unittest.TestCase):
    @mock.patch("os.path")
    def test_is_installed(self, mock_path):
        mock_path.abspath.return_value = "ocr/setup.py"
        mock_path.dirname.return_value = "ocr"
        mock_path.join.return_value = "ocr/" + ONG_FOLDER
        is_installed()
        mock_path.dirname.assert_called_with("ocr/setup.py")
        mock_path.join.assert_called_with("ocr", ONG_FOLDER)
        mock_path.isdir.assert_called_with("ocr/" + ONG_FOLDER)
        mock_path.isdir.return_value = True
        self.assertTrue(is_installed())
        mock_path.isdir.return_value = False
        self.assertFalse(is_installed())

    @mock.patch("ocr.setup.engine")
    @mock.patch("ocr.setup.Base")
    def test_create_tables(self, mock_base, mock_engine):
        create_tables()
        mock_engine.execute.assert_called_with("USE `%s`" % BD_NAME)
        mock_base.metadata.create_all.assert_called_with(mock_engine)

    @mock.patch("ocr.setup.engine")
    def test_create_database(self, mock_engine):
        create_database()
        mock_engine.execute.assert_called_with('CREATE DATABASE IF NOT EXISTS `%s`' % BD_NAME)

    @mock.patch("os.path")
    @mock.patch("os.mkdir")
    def test_new_ong_dir(self, mock_mkdir, mock_path):
        mock_path.abspath.return_value = "ocr/setup.py"
        mock_path.dirname.return_value = "ocr"
        mock_path.join.return_value = "ocr/" + ONG_FOLDER
        new_ong_dir()
        mock_path.dirname.assert_called_with("ocr/setup.py")
        mock_path.join.assert_called_with("ocr", ONG_FOLDER)
        mock_mkdir.assert_called_with("ocr/" + ONG_FOLDER)


if __name__ == '__main__':
    unittest.main(buffer=True)