import os
import shutil
import sqlalchemy

from config import ONG_FOLDER, BD_HOST, BD_PASSWORD, BD_USER, BD_NAME

origin = os.path.dirname(os.path.abspath(__file__))
destiny = os.getcwd()

print "Create ONG directory."
os.mkdir(os.path.join(destiny, ONG_FOLDER))

templateo = os.path.join(origin, "templates")
templated = os.path.join(destiny, "templates")
print "Create template directory."
shutil.copytree(templateo, templated)

print "Create database %s" % BD_NAME
engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (BD_USER, BD_PASSWORD, BD_HOST))
engine.execute("CREATE DATABASE `%s`" % BD_NAME)
engine.execute("USE `%s`" % BD_NAME)