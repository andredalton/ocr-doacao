#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

import xmltodict

from sqlalchemy.orm import exc
from sqlalchemy import Column, String, Sequence, UniqueConstraint, or_
from sqlalchemy.dialects.mysql import INTEGER

from . import Persistence, Base
from ..config import ONG_FOLDER
from ..functions import file_get_contents, warning


class Ong(Persistence):
    def __init__(self, session=None, id=None, name=None, complete_name=None, homepage=None, image=None, css=None):
        if id is None:
            self.id = None
        else:
            self.id = int(id)
        self.name = name
        self.complete_name = complete_name
        self.homepage = homepage
        self.image = image
        self.css = css
        self.db = OngBD(id=id, name=self.name)
        if session is None:
            warning("This object is not be able to persist in BD.")
        else:
            self.session = session

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_complete_name(self):
        return self.complete_name

    def get_homepage(self):
        return self.homepage

    def get_image(self):
        return self.image

    def get_css(self):
        return self.css

    def set_name(self, name):
        self.name = name

    def exist_ong_dir(self):
        return os.path.isdir(os.path.join(ONG_FOLDER, self.name))

    def load(self):
        db = self.load_db()
        xml = self.load_xml()
        return db and xml

    def load_xml(self):
        try:
            content = xmltodict.parse(file_get_contents(os.path.join(ONG_FOLDER, self.name, "ong.xml")))['ong']
        except AttributeError:
            warning("Try open ong xml without name.")
            return False
        except IOError:
            warning("Invalid name.")
            return False
        self.name = content['name']
        self.complete_name = content['completename']
        self.homepage = content['homepage']
        self.image = content['image']
        self.css = content['css']
        return True

    def load_db(self):
        try:
            q = self.session.query(OngBD).filter(or_(OngBD.id == self.id, OngBD.name == self.name)).one()
        except UnboundLocalError:
            warning("Try search in database without ong name or id.")
            return False
        except exc.NoResultFound:
            warning("Ong [%s, %s] not found." % (self.id, self.name))
            return False
        except exc.MultipleResultsFound:
            warning("Multiple results found for ong [%s, %s]." % (self.id, self.name))
            return False
        self.id = q.id
        if self.name is not None and q.name != self.name:
            warning("Name passed was overwritten by name in the database.")
        self.name = q.name
        return True

    def flush_db(self):
        self.db.name = self.name

    def delete(self):
        if self.session is None:
            return False
        try:
            ong = self.session.query(OngBD).filter(or_(OngBD.id == self.id, OngBD.name == self.name)).one()
        except UnboundLocalError:
            warning("Try search in database without ong name or id.")
            return False
        except exc.NoResultFound:
            warning("Ong [%s, %s] not found." % (self.id, self.name))
            return False
        except exc.MultipleResultsFound:
            warning("Multiple results found for ong [%s, %s]." % (self.id, self.name))
            return False
        try:
            self.session.delete(ong)
            self.session.commit()
        except exc.InvalidRequestError as e:
            print "Delete from DB fail."
            self.session.rollback()
            return False
        return True


class OngBD(Base):
    __tablename__ = 'ong'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    UniqueConstraint('name', name='unique_name')

    def __repr__(self):
        return "<ONG(id=%c, name='%s')>" % (
            self.id, self.name)