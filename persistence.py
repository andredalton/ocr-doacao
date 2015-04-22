#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

import xmltodict
from shutil import rmtree

from werkzeug import secure_filename
from uuid import uuid4
from sqlalchemy.orm import exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Sequence, CHAR, DateTime, Float, Text, UniqueConstraint, Index, TIMESTAMP, or_
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import ONG_FOLDER, UPLOAD_FOLDER, BD_NAME, BD_PASSWORD, BD_USER, BD_HOST, HOST, IMG_NAME
from functions import file_get_contents, warning, make_md5


def create_session():
    engine = create_engine("mysql+pymysql://%s:%s@%s/%s" % (BD_USER, BD_PASSWORD, BD_HOST, BD_NAME))
    session = sessionmaker(bind=engine)()
    return session


Base = declarative_base()


class Persistence():
    def __init__(self, session=None):
        self.db = Base
        self.session = session

    def flush_db(self):
        pass

    def add_bd(self):
        if self.session is None:
            return False
        self.flush_db()
        self.session.add(self.db)
        try:
            self.session.commit()
        except IntegrityError as e:
            print e
            print "Add to DB fail."
            return False
        return True

    def load(self):
        warning("Method load is not implemented.")
        return False

    def save(self):
        warning("Method save is not implemented.")
        return False

    def delete(self):
        warning("Method delete is not implemented.")
        return False

    def search(self):
        warning("Method search is not implemented.")
        return False


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
        return db or xml

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


class OngBD(Base):
    __tablename__ = 'ong'
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    UniqueConstraint('name', name='unique_name')

    def __repr__(self):
        return "<ONG(id=%c, name='%s', homepage='%s')>" % (
            self.id, self.name, self.homepage)


class Image(Persistence):
    def __init__(self, session=None, id=None, id_ong=None, ong_name=None, path=None, md5=None, fd=None):
        self.id = id
        self.id_ong = id_ong
        self.ong_name = ong_name
        self.path = path
        self.md5 = md5
        self.text = None
        self.cnpj = None
        self.coo = None
        self.data = None
        self.total = None
        self.hora_envio = None
        self.db = ImageBD(id_ong=self.id_ong, path=self.path, md5=self.md5, text=self.text, cnpj=self.cnpj,
                          coo=self.coo, data=self.data, total=self.total, hora_envio=self.hora_envio)
        self.session = session
        self.fd = fd
        if fd is not None:
            (self.fname, self.fextension) = os.path.splitext(fd.filename)
        else:
            self.fname = None
            self.fextension = None
        if self.id_ong is None and self.ong_name is not None:
            pass
        o = Ong(self.session, id=self.id_ong, name=self.ong_name)
        o.load()
        self.id_ong = o.get_id()

    def flush_db(self):
        self.db.id_ong = self.id_ong
        self.db.md5 = self.md5
        self.db.path = os.path.join(HOST, self.path, IMG_NAME + self.fextension)
        self.db.text = self.text

    def unlink(self):
        rmtree(self.path)

    def get_extension(self):
        return self.fextension

    def get_path(self):
        return self.path

    def new_path(self):
        new_dir = os.path.join(ONG_FOLDER, self.ong_name, UPLOAD_FOLDER, str(uuid4()))
        os.mkdir(new_dir, 0744)
        self.path = new_dir

    def load_db(self):
        try:
            q = self.session.query(ImageBD).filter(or_(ImageBD.id == self.id, ImageBD.md5 == self.md5,
                                                       ImageBD.path == self.path)).one()
        except UnboundLocalError:
            warning("Try search in database without image path, md5 or id.")
            return False
        except exc.NoResultFound:
            warning("Image [%d, %s, %s] not found." % (self.id, self.md5, self.path))
            return False
        except exc.MultipleResultsFound:
            warning("Multiple results found for ong [%d, %s, %s]." % (self.id, self.md5, self.path))
            return False
        self.id = q.id
        if self.md5 is not None and q.md5 != self.md5:
            warning("MD5 passed was overwritten by md5 in the database.")
        if self.path is not None and q.path != self.path:
            warning("Path passed was overwritten by path in the database.")
        self.md5 = q.md5
        self.path = q.path
        return True

    def save(self):
        if self.fd is None:
            return False
        filename = secure_filename(self.fd.filename)
        (name, self.fextension) = os.path.splitext(filename)
        self.new_path()
        self.fd.save(os.path.join(self.path, IMG_NAME + self.fextension))
        self.md5 = make_md5(os.path.join(self.path, IMG_NAME), self.fextension)
        if not self.add_bd():
            self.unlink()
            return False
        return True


class ImageBD(Base):
    __tablename__ = 'image'
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    id_ong = Column(INTEGER(unsigned=True), default=0)
    path = Column(String(255), default="")
    md5 = Column(CHAR(32), default="")
    text = Column(Text, default="",  nullable=True)
    cnpj = Column(String(255), default=None, nullable=True)
    coo = Column(String(255), default=None, nullable=True)
    data = Column(DateTime, default=None, nullable=True)
    total = Column(Float, default=None, nullable=True)
    hora_envio = Column(TIMESTAMP)
    UniqueConstraint('path', name='path')
    UniqueConstraint('md5', name='md5')
    Index('id_ong')

    def __repr__(self):
        return "<ONG(name='%s', homepage='%s')>" % (
            self.name, self.homepage)