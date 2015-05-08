#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock
import sys
import os
from sqlalchemy.orm import exc
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", "..", ".."))
from ocr.persistence.ong import Ong, OngBD
from ocr.config import ONG_FOLDER


class TestOng(unittest.TestCase):
    def setUp(self):
        self.o = Ong(name="anyOng")

    @mock.patch("ocr.persistence.ong.warning")
    def test__init__(self, mock_warning):
        o = Ong()
        self.assertIsNone(o.session)
        self.assertIsNone(o.id)
        self.assertIsNone(o.name)
        mock_warning.assert_called_with('This object is not be able to persist in BD.')
        o = Ong("session", 42, "anyName")
        self.assertEqual(o.session, "session")
        self.assertEqual(o.id, 42)
        self.assertEqual(o.name, "anyName")

    def test_get_id(self):
        o = Ong()
        self.assertIsNone(o.get_id())
        o = Ong(id=42)
        self.assertEqual(o.get_id(), 42)

    def test_get_name(self):
        o = Ong()
        self.assertIsNone(o.get_name())
        o = Ong(name="anyName")
        self.assertEqual(o.get_name(), "anyName")

    @mock.patch("ocr.persistence.ong.os")
    def test_exist_ong_dir(self, mock_os):
        mock_os.getcwd.return_value = "/home/ocr"
        mock_os.path.join.return_value = "/home/ocr/ocr" + ONG_FOLDER + "/anyOng"
        mock_os.path.isdir.return_value = True
        self.assertTrue(self.o.exist_ong_dir())
        mock_os.getcwd.assert_called_with()
        mock_os.path.join.assert_called_with("/home/ocr", 'ocr', ONG_FOLDER, 'anyOng')
        mock_os.path.isdir.assert_called_with("/home/ocr/ocr" + ONG_FOLDER + "/anyOng")

    @mock.patch("ocr.persistence.ong.Ong._load_db")
    @mock.patch("ocr.persistence.ong.Ong.exist_ong_dir")
    def test_load(self, mock_dir, mock_load):
        mock_dir.return_value = True
        mock_load.return_value = True
        self.assertTrue(self.o.load())
        mock_load.return_value = False
        self.assertFalse(self.o.load())
        mock_dir.return_value = False
        self.assertFalse(self.o.load())
        mock_load.return_value = True
        self.assertFalse(self.o.load())

    @mock.patch("ocr.persistence.ong.warning")
    def test_get_one(self, mock_warning):
        mock_one = mock.Mock()
        mock_one.one.return_value = True
        mock_filter = mock.Mock()
        mock_filter.filter.return_value = mock_one
        mock_session = mock.Mock()
        mock_session.query.return_value = mock_filter
        self.o.session = mock_session
        self.assertTrue(self.o._get_one())
        mock_one.one.assert_called_with()
        self.assertTrue(mock_filter.filter.called)
        mock_session.query.assert_called_with(OngBD)
        mock_session.query.side_effect = UnboundLocalError()
        self.assertFalse(self.o._get_one())
        mock_warning.assert_called_with('Try search in database without ong name or id.')
        mock_session.query.side_effect = exc.NoResultFound()
        self.assertFalse(self.o._get_one())
        mock_warning.assert_called_with('Ong [None, anyOng] not found.')
        mock_session.query.side_effect = exc.MultipleResultsFound()
        self.assertFalse(self.o._get_one())
        mock_warning.assert_called_with('Multiple results found for ong [None, anyOng].')

    @mock.patch("ocr.persistence.ong.Ong._get_one")
    @mock.patch("ocr.persistence.ong.warning")
    def test_load_db(self, mock_warning, mock_get_one):
        mock_get_one.return_value = False
        self.assertFalse(self.o._load_db())
        mock_one = mock.Mock()
        mock_one.id = 42
        self.o.name = "anyName"
        mock_one.name = "otherName"
        mock_get_one.return_value = mock_one
        mock_session = mock.Mock()
        self.o.session = mock_session
        self.assertTrue(self.o._load_db())
        mock_warning.assert_called_with('Name passed was overwritten by name in the database.')
        mock_session.commit.assert_called_with()
        self.assertEqual(self.o.id, 42)
        self.assertEqual(self.o.name, "otherName")

    def test__flush_db(self):
        o = Ong(name="anyName")
        o._flush_db()
        self.assertEqual(o.name, o.db.name)

    @mock.patch("ocr.persistence.ong.shutil")
    @mock.patch("ocr.persistence.ong.os")
    @mock.patch("ocr.persistence.ong.warning")
    @mock.patch("ocr.persistence.ong.Ong._get_one")
    def test_delete(self, mock_get_one, mock_warning, mock_os, mock_shutil):
        self.o.name = "anyName"
        self.o.session = None
        self.assertFalse(self.o.delete())
        mock_session = mock.Mock()
        mock_session.delete.side_effect = exc.UnmappedInstanceError(1)
        self.o.session = mock_session
        mock_get_one.return_value = "anyOng"
        self.assertFalse(self.o.delete())
        mock_session.rollback.assert_called_with()
        mock_warning.assert_called_with('Delete from DB fail.')
        mock_session.delete.side_effect = None
        mock_os.getcwd.return_value = "/home/ocr"
        mock_os.path.join.return_value = '/home/ocr/ocr' + ONG_FOLDER + '/anyName'
        self.assertTrue(self.o.delete())
        mock_os.getcwd.assert_called_with()
        mock_os.path.join.assert_called_with('/home/ocr', 'ocr', ONG_FOLDER, 'anyName')
        mock_shutil.rmtree.assert_called_with('/home/ocr/ocr' + ONG_FOLDER + '/anyName')
        mock_shutil.rmtree.side_effect = OSError()
        self.assertFalse(self.o.delete())
        mock_warning.assert_called_with('The ONG directory does not exists')

    @mock.patch("ocr.persistence.ong.os")
    @mock.patch("ocr.persistence.ong.Ong.add_db")
    def test_save(self, mock_add_db, mock_os):
        self.o.name = "anyName"
        self.o.session = None
        self.assertFalse(self.o.save())
        self.o.session = True
        mock_add_db.return_value = True
        mock_os.getcwd.return_value = "/home/ocr"
        mock_os.path.join.return_value = '/home/ocr/ocr/' + ONG_FOLDER + '/anyName'
        self.assertTrue(self.o.save())
        mock_os.getcwd.assert_called_with()
        mock_os.path.join.assert_called_with('/home/ocr', 'ocr', ONG_FOLDER, 'anyName')
        mock_os.mkdir.assert_called_with('/home/ocr/ocr/' + ONG_FOLDER + '/anyName')
        mock_add_db.return_value = False
        self.assertFalse(self.o.save())
        mock_os.rmdir.assert_called_with('/home/ocr/ocr/' + ONG_FOLDER + '/anyName')


class TestOngBD(unittest.TestCase):
    def setUp(self):
        self.db = OngBD()

    def test__repr__(self):
        self.db.id = 42
        self.db.name = "ongName"
        self.assertEqual(self.db.__repr__(), "<ONG(id=42, name='ongName')>")

if __name__ == '__main__':
    unittest.main(buffer=True)