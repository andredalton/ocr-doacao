import os
import sqlalchemy

from config import ONG_FOLDER, BD_HOST, BD_PASSWORD, BD_USER, BD_NAME
from persistence import Base

engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (BD_USER, BD_PASSWORD, BD_HOST),  encoding='utf8')


def is_installed():
    local = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(local, ONG_FOLDER)):
        return True
    return False


def new_ong_dir():
    local = os.path.dirname(os.path.abspath(__file__))
    print "Create ONG directory."
    os.mkdir(os.path.join(local, ONG_FOLDER))


def create_database():
    print "Create database %s" % BD_NAME
    engine.execute("CREATE DATABASE IF NOT EXISTS `%s`" % BD_NAME)


def create_tables():
    print "Create tables at %s" % BD_NAME
    engine.execute("USE `%s`" % BD_NAME)
    from persistence.ong import OngBD
    from persistence.image import ImageBD
    Base.metadata.create_all(engine)