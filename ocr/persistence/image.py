#!/usr/bin/python
# -*- coding: UTF8 -*-

import datetime
import os

from shutil import rmtree

from werkzeug import secure_filename
from uuid import uuid4
from sqlalchemy.orm import exc
from sqlalchemy import Column, String, Sequence, CHAR, DateTime, UniqueConstraint, Index, Enum, ForeignKey, or_
from sqlalchemy.dialects.mysql import INTEGER

from . import Persistence, Base
from ong import Ong
from meta_image import MetaImage
from ..config import ONG_FOLDER, HOST, IMG_NAME
from ..functions import make_md5, warning


class Image(Persistence):
    def __init__(self, session=None, ong_name=None, id=None, fd=None):
        self.session = session
        self.id = id
        self.ong_name = ong_name
        self.path = None
        self.md5 = None
        self.send_time = None
        self.status = None
        if id is not None:
            self.id = id
            self.load()
        else:
            o = Ong(self.session, name=self.ong_name)
            o.load()
            self.id_ong = o.get_id()
        self.db = ImageBD(id_ong=self.id_ong, path=self.path, md5=self.md5, send_time=self.send_time)
        self.fd = fd
        if fd is not None:
            (self.fname, self.fextension) = os.path.splitext(fd.filename)
        else:
            self.fname = None
            self.fextension = None
        self.complete_path = None

    def _flush_db(self):
        self.db.id = self.id
        self.db.id_ong = self.id_ong
        self.db.md5 = self.md5
        self.db.path = os.path.join(HOST, self.path, IMG_NAME + self.fextension)

    def __unlink(self):
        rmtree(self.complete_path)

    def __new_path(self):
        package = __name__.split(".")[0]
        new_dir = os.path.join(self.ong_name, str(uuid4()))
        self.complete_path = os.path.join(os.getcwd(), package, ONG_FOLDER, new_dir)
        os.mkdir(self.complete_path, 0744)
        self.path = os.path.join(HOST, new_dir)

    def load(self):
        try:
            q = self.session.query(ImageBD).filter(or_(
                ImageBD.id == self.id,
                ImageBD.md5 == self.md5,
                ImageBD.path == self.path
            )).one()
        except UnboundLocalError:
            warning("Try search in database without image id, md5 or path.")
            return False
        except exc.NoResultFound:
            warning("Image [%d, %s, %s] not found." % (self.id, self.md5, self.path))
            return False
        except exc.MultipleResultsFound:
            warning("Multiple results found for image [%d, %s, %s]." % (self.id, self.md5, self.path))
            return False
        self.id = q.id
        self.path = q.path
        self.md5 = q.md5
        self.id_ong = q.id_ong
        self.send_time = q.send_time
        self.status = q.status
        self.session.commit()

    def save(self):
        if self.fd is None:
            return False
        filename = secure_filename(self.fd.filename)
        (name, self.fextension) = os.path.splitext(filename)
        self.__new_path()
        self.fd.save(os.path.join(self.complete_path, IMG_NAME + self.fextension))
        self.md5 = make_md5(os.path.join(self.complete_path, IMG_NAME), self.fextension)
        if not self.add_db():
            self.__unlink()
            return False
        m = MetaImage(session=self.session, id_image=self.db.id, id_ong=self.id_ong)
        if not m.save():
            warning("Fail to create meta_image.")
        return True

    def search(self):
        now = datetime.datetime.now()
        if now.day < 20:
            if now.month > 1:
                fday = datetime.date(now.year, now.month - 1, 1)
            else:
                fday = datetime.date(now.year - 1, 12, 1)
        else:
            fday = datetime.date(now.year, now.month, 1)
        lst = []
        for path, send_time in self.session.query(ImageBD.path, ImageBD.send_time).\
                filter(ImageBD.id_ong == self.id_ong, ImageBD.send_time >= fday).order_by(ImageBD.send_time).all():
            lst.append({'path': path, 'send_time': str(send_time)})
        self.session.commit()
        return lst


class ImageBD(Base):
    __tablename__ = 'image'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(INTEGER(unsigned=True), Sequence('user_id_seq'), primary_key=True)
    id_ong = Column(INTEGER(unsigned=True), ForeignKey("ong.id", onupdate="CASCADE", ondelete="CASCADE"), default=0,
                    nullable=False)
    path = Column(String(collation='utf8_general_ci', length=255), default="", nullable=False, unique=True)
    md5 = Column(CHAR(collation='utf8_general_ci', length=32), default="", nullable=False, unique=True)
    send_time = Column(DateTime, default=datetime.datetime.now, nullable=False)
    status = Column(Enum(u'preprocessing', u'processing', u'processed'), nullable=False, default=u'preprocessing', server_default=u'preprocessing')
    UniqueConstraint('path', name='path')
    UniqueConstraint('md5', name='md5')
    Index('id_ong')

    def __repr__(self):
        return "<IMAGE(id=%d, id_ong=%d, path='%s', md5='%s', send_time='%s')>" % (
            self.id, self.id_ong, self.path, self.md5, self.send_time)