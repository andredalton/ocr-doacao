#!/usr/bin/python
# -*- coding: UTF8 -*-

import os
import shutil

from sqlalchemy.orm import exc
from sqlalchemy import Column, String, Sequence, UniqueConstraint, or_
from sqlalchemy.dialects.mysql import INTEGER

from . import Persistence, Base
from ..config import ONG_FOLDER
from ..functions import warning


class Ong(Persistence):
    def __init__(self, session=None, id=None, name=None):
        self.id = None
        if id is not None:
            self.id = int(id)
        self.name = None
        if name is not None:
            self.name = str(name)
        self.db = OngBD(id=self.id, name=self.name)
        if session is None:
            warning("This object is not be able to persist in BD.")
            self.session = None
        else:
            self.session = session

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def exist_ong_dir(self):
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        return os.path.isdir(ong_dir)

    def load(self):
        db = self._load_db()
        path = self.exist_ong_dir()
        return db and path

    def _get_one(self):
        try:
            return self.session.query(OngBD).filter(or_(OngBD.id == self.id, OngBD.name == self.name)).one()
        except UnboundLocalError:
            warning("Try search in database without ong name or id.")
            return False
        except exc.NoResultFound:
            warning("Ong [%s, %s] not found." % (self.id, self.name))
            return False
        except exc.MultipleResultsFound:
            warning("Multiple results found for ong [%s, %s]." % (self.id, self.name))
            return False

    def _load_db(self):
        q = self._get_one()
        if not q:
            return False
        self.id = q.id
        if self.name is not None and q.name != self.name:
            warning("Name passed was overwritten by name in the database.")
        self.name = q.name
        self.session.commit()
        return True

    def _flush_db(self):
        self.db.name = self.name

    def delete(self):
        if self.session is None:
            return False
        ong = self._get_one()
        try:
            self.session.delete(ong)
            self.session.commit()
        except exc.UnmappedInstanceError:
            warning("Delete from DB fail.")
            self.session.rollback()
            return False
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        try:
            shutil.rmtree(ong_dir)
        except OSError:
            warning("The ONG directory does not exists")
            return False
        return True

    def save(self):
        if self.session is None:
            return False
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        os.mkdir(ong_dir)
        if not self.add_db():
            os.rmdir(ong_dir)
            return False
        return True


class OngBD(Base):
    __tablename__ = 'ong'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    name = Column(String(collation='utf8_general_ci', length=50), nullable=False, unique=True)
    UniqueConstraint('name', name='unique_name')

    def __repr__(self):
        return "<ONG(id=%d, name='%s')>" % (
            self.id, self.name)