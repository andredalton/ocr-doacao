#!/usr/bin/python
# -*- coding: UTF8 -*-

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..functions import warning
from ..config import BD_NAME, BD_USER, BD_HOST, BD_PASSWORD

Base = declarative_base()


class Session():
    def __init__(self):
        self.engine = create_engine("mysql+pymysql://%s:%s@%s/%s" % (BD_USER, BD_PASSWORD, BD_HOST, BD_NAME),
                                    encoding='utf8', pool_size=100, pool_recycle=7200)
        self.session = sessionmaker(bind=self.engine)()

    def get_session(self):
        return self.session

    def get_engine(self):
        return self.engine


class Persistence():
    def __init__(self, session=None):
        self.db = Base
        if session is not None:
            self.session = session.get_session()
        else:
            self.session = None
            warning("This persistence can`t access the database.")

    def _flush_db(self):
        raise NotImplementedError()

    def add_db(self):
        if self.session is None:
            return False
        self._flush_db()
        try:
            self.session.add(self.db)
            self.session.commit()
        except IntegrityError as e:
            warning("Add to DB fail.")
            self.session.rollback()
            return False
        return True

    def load(self):
        raise NotImplementedError()

    def save(self):
        return self.add_db()

    def delete(self):
        raise NotImplementedError()

    def search(self):
        raise NotImplementedError()