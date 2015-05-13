#!/usr/bin/python
# -*- coding: UTF8 -*-

import datetime

from sqlalchemy.orm import exc
from sqlalchemy import Column, String, DateTime, Index, ForeignKey, or_, and_
from sqlalchemy.dialects.mysql import INTEGER, FLOAT
from sqlalchemy.types import Enum

from . import Persistence, Base
from ..config import EDIT_TIME

class MetaImage(Persistence):
    def __init__(self, session=None, id_ong=None, id_image=None):
        self.id_image = id_image
        self.id_ong = id_ong
        self.coo = None
        self.cnpj = None
        self.data = None
        self.total = None
        self.session = session
        self.status = "no analyzed"
        self.update_time = None
        self.db = MetaImageBD(id_image=self.id_image)

    def _flush_db(self):
        self.db.id_image = self.id_image
        self.db.id_ong = self.id_ong
        self.db.coo = self.coo
        self.db.cnpj = self.cnpj
        self.db.data = self.data
        self.db.total = self.total
        self.db.status = self.status

    def update(self):
        q = self.session.query(MetaImageBD).filter(MetaImageBD.id_image == self.id_image).one()
        q.id_ong = self.id_ong
        q.coo = self.coo
        q.cnpj = self.cnpj
        q.total = self.total
        q.status = self.status
        try:
            q.data = datetime.datetime.strptime(self.data, "%d/%m/%Y")
            self.session.commit()
            return True
        except ValueError:
            self.session.rollback()
            return False

    def load(self):
        q = self.session.query(MetaImageBD).filter(MetaImageBD.id_image == self.id_image).one()
        self.id_ong = q.id_ong
        self.coo = q.coo
        self.cnpj = q.cnpj
        self.data = q.data
        self.total = q.total
        self.status = q.status
        self.session.commit()

    def _get_one(self):
        now = datetime.datetime.now()
        start = now - datetime.timedelta(minutes=EDIT_TIME)
        if now.day < 20:
            if now.month > 1:
                fday = datetime.date(now.year, now.month - 1, 1)
            else:
                fday = datetime.date(now.year - 1, 12, 1)
        else:
            fday = datetime.date(now.year, now.month, 1)
        return self.session.query(MetaImageBD).filter(
            and_(
                MetaImageBD.id_ong == self.id_ong,
                or_(
                    and_(
                        MetaImageBD.status == "no analyzed",
                        MetaImageBD.update_time >= fday
                    ),
                    and_(
                        MetaImageBD.status == "analyzing",
                        MetaImageBD.update_time <= start
                    )
                )
            )
        ).order_by(MetaImageBD.id_image)

    def count(self):
        return self._get_one().count()

    def search(self):
        try:
            q = self._get_one().limit(1).one()
        except exc.NoResultFound:
            return False
        q.status = "analyzing"
        q.update_time = datetime.datetime.now()
        self.id_image = q.id_image
        self.id_ong = q.id_ong
        self.coo = q.coo
        self.cnpj = q.cnpj
        self.data = q.data
        self.total = q.total
        self.status = q.status
        self.session.commit()
        return True


class MetaImageBD(Base):
    __tablename__ = 'meta_image'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id_image = Column(INTEGER(unsigned=True), ForeignKey("image.id", onupdate="CASCADE", ondelete="CASCADE"), default=0,
                      nullable=False, primary_key=True)
    id_ong = Column(INTEGER(unsigned=True), ForeignKey("ong.id", onupdate="CASCADE", ondelete="CASCADE"), default=0,
                      nullable=False, index=True)
    coo = Column(String(collation='utf8_general_ci', length=20), default=None, nullable=True)
    cnpj = Column(String(collation='utf8_general_ci', length=20), default=None, nullable=True)
    data = Column(DateTime, default=None, nullable=True)
    total = Column(FLOAT(unsigned=True), default=None, nullable=True)
    status = Column(Enum(u'no analyzed', u'analyzing', u'valid', u'invalid'), nullable=False, default=u'no analyzed', server_default=u'no analyzed')
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    Index('id_ong')

    def __repr__(self):
        return "<META_IMAGE(id_image=%d, coo='%s', cnpj='%s', data='%s', total=%f)>" % (
            self.id_image, self.coo, self.cnpj, self.data, self.total)