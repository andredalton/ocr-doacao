#!/usr/bin/python
# -*- coding: UTF8 -*-

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import BD_NAME, BD_USER, BD_HOST, BD_PASSWORD

Base = declarative_base()


class Session():
    def __init__(self):
        self.engine = create_engine("mysql+pymysql://%s:%s@%s/%s" % (BD_USER, BD_PASSWORD, BD_HOST, BD_NAME))
        self.session = sessionmaker(bind=self.engine)()

    def get_session(self):
        return self.session

    def get_engine(self):
        return self.engine


class Persistence():
    def __init__(self, session=None):
        self.db = Base
        self.session = session.get_session()

    def flush_db(self):
        pass

    def add_bd(self):
        if self.session is None:
            return False
        self.flush_db()
        print self.session
        print self.session.__class__
        print self.session.__dict__
        self.session.add(self.db)
        try:
            self.session.commit()
        except IntegrityError as e:
            print e
            print "Add to DB fail."
            self.session.rollback()
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