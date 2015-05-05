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
        if id is None:
            self.id = None
        else:
            self.id = int(id)
        self.name = name
        self.db = OngBD(id=id, name=self.name)
        if session is None:
            warning("This object is not be able to persist in BD.")
        else:
            self.session = session

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def exist_ong_dir(self):
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        return os.path.isdir(ong_dir)

    def load(self):
        db = self.load_db()
        path = self.exist_ong_dir()
        return db and path

    def get_one(self):
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

    def load_db(self):
        q = self.get_one()
        if q == False:
            return False
        self.id = q.id
        if self.name is not None and q.name != self.name:
            warning("Name passed was overwritten by name in the database.")
        self.name = q.name
        self.session.commit()
        return True

    def flush_db(self):
        self.db.name = self.name

    def delete(self):
        if self.session is None:
            return False
        ong = self.get_one()
        try:
            self.session.delete(ong)
            self.session.commit()
        except exc.UnmappedInstanceError as e:
            print "Delete from DB fail."
            self.session.rollback()
            return False
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        try:
            shutil.rmtree(ong_dir)
        except OSError:
            print "The ONG directory does not exists"
            return False
        return True

    def save(self):
        if self.session is None:
            return False
        package = __name__.split(".")[0]
        ong_dir = os.path.join(os.getcwd(), package, ONG_FOLDER, self.name)
        os.mkdir(ong_dir)
        if not self.add_bd():
            os.rmdir(ong_dir)
            return False
        return True

class OngBD(Base):
    __tablename__ = 'ong'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    UniqueConstraint('name', name='unique_name')

    def __repr__(self):
        return "<ONG(id=%c, name='%s')>" % (
            self.id, self.name)