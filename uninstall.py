import os
import shutil
import sqlalchemy

from ocr.config import ONG_FOLDER, BD_HOST, BD_PASSWORD, BD_USER, BD_NAME

origin = os.path.dirname(os.path.abspath(__file__))
destiny = os.getcwd()

print "Delete ONG directory."
shutil.rmtree(os.path.join(destiny, ONG_FOLDER))

print "Remove database %s" % BD_NAME
engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (BD_USER, BD_PASSWORD, BD_HOST))
engine.execute("DROP DATABASE `%s`" % BD_NAME)