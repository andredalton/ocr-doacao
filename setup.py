import os
import shutil

import sqlalchemy

from ocr.config import ONG_FOLDER, BD_HOST, BD_PASSWORD, BD_USER, BD_NAME

origin = os.path.dirname(os.path.abspath(__file__))
destiny = os.getcwd()

print "Create ONG directory."
os.mkdir(os.path.join(destiny, ONG_FOLDER))

print "Create template directory."
templateo = os.path.join(origin, "ocr", "templates")
templated = os.path.join(destiny, "templates")
shutil.copytree(templateo, templated)

print "Create database %s" % BD_NAME
engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (BD_USER, BD_PASSWORD, BD_HOST),  encoding='utf8')
engine.execute("CREATE DATABASE IF NOT EXISTS `%s`" % BD_NAME)
engine.execute("USE `%s`" % BD_NAME)

print "Create tables at %s" % BD_NAME
from ocr.persistence import Base
from ocr.persistence.ong import OngBD
from ocr.persistence.image import ImageBD

Base.metadata.create_all(engine)