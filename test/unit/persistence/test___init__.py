#!/usr/bin/python
# -*- coding: UTF8 -*-
import unittest
import mock

import sys
import os
from sqlalchemy.exc import IntegrityError
local = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(local, "..", "..", ".."))
from ocr.persistence import Session, Persistence, Base
from ocr.config import BD_USER, BD_PASSWORD, BD_HOST, BD_NAME


class TestSession(unittest.TestCase):
    @mock.patch("ocr.persistence.create_engine")
    @mock.patch("ocr.persistence.sessionmaker")
    def config(self, mock_sessionmaker, mock_create_engine):
        self.mock_sessionmaker = mock_sessionmaker
        self.mock_create_engine = mock_create_engine
        self.mock_create_engine.return_value = "engine"
        self.mock_session = mock.Mock()
        self.mock_session.return_value = "session"
        self.mock_sessionmaker.return_value = self.mock_session
        self.session = Session()

    def setUp(self):
        self.mock_sessionmaker = None
        self.mock_create_engine = None
        self.mock_session = None
        self.session = None
        self.config()

    def test___init__(self):
        self.mock_create_engine.assert_called_with('mysql+pymysql://%s:%s@%s/%s' % (BD_USER, BD_PASSWORD, BD_HOST,
                                                                                    BD_NAME),
                                                   pool_recycle=7200, encoding='utf8', pool_size=100)
        self.mock_sessionmaker.assert_called_with(bind="engine")

    def test_get_session(self):
        self.assertEqual("session", self.session.get_session())

    def test_get_engine(self):
        self.assertEqual("engine", self.session.get_engine())


class TestPersistence(unittest.TestCase):
    def setUp(self):
        mock_session = mock.Mock()
        mock_session.get_session.return_value = "session"
        self.persistence = Persistence(mock_session)

    @mock.patch("ocr.persistence.warning")
    def test___init__(self, mock_warning):
        Persistence()
        mock_warning.assert_called_with("This persistence can`t access the database.")
        mock_session = mock.Mock()
        Persistence(mock_session)
        mock_session.get_session.assert_called_with()

    def test_flush_db(self):
        with self.assertRaises(NotImplementedError):
            self.persistence._flush_db()

    @mock.patch("ocr.persistence.Persistence._flush_db")
    def test_add_db(self, mock_flush):
        p = Persistence()
        self.assertFalse(p.add_db())
        mock_session = mock.Mock()
        mock_sessionobj = mock.Mock()
        mock_sessionobj.get_session.return_value = mock_session
        p = Persistence(mock_sessionobj)
        self.assertTrue(p.add_db())
        mock_flush.assert_called_with()
        mock_session.add.assert_called_with(Base)
        mock_session.commit.assert_called_with()
        mock_session.add.side_effect = IntegrityError(1, 2, 3)
        self.assertFalse(p.add_db())
        mock_session.rollback.assert_called_with()

    def test_load(self):
        with self.assertRaises(NotImplementedError):
            self.persistence.load()

    @mock.patch("ocr.persistence.Persistence.add_db")
    def test_save(self, mock_add_db):
        self.persistence.save()
        mock_add_db.assert_called_with()
        mock_add_db.return_value = True
        self.assertTrue(self.persistence.save())
        mock_add_db.return_value = False
        self.assertFalse(self.persistence.save())

    def test_delete(self):
        with self.assertRaises(NotImplementedError):
            self.persistence.delete()

    def test_search(self):
        with self.assertRaises(NotImplementedError):
            self.persistence.search()

if __name__ == '__main__':
    unittest.main(buffer=True)