#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

from shutil import rmtree

from werkzeug import secure_filename
from uuid import uuid4
from sqlalchemy.orm import exc
from sqlalchemy import Column, String, Sequence, CHAR, DateTime, Float, Text, UniqueConstraint, Index, TIMESTAMP, or_
from sqlalchemy.dialects.mysql import INTEGER

from . import Persistence, Base
from .ong import Ong
from ..__init__ import ONG_FOLDER, UPLOAD_FOLDER, HOST, IMG_NAME, file_get_contents, warning, make_md5


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
        print new_dir
        print os.getcwd()
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
        return "<IMAGE(id=%d, id_ong=%d, path='%s', md5='%s', text='%s', cnpj='%s', coo='%s', data='%s', total, hora_envio)>" % (
            self.name, self.homepage)