import os
import shutil
import sqlalchemy

from .config import ONG_FOLDER, BD_HOST, BD_PASSWORD, BD_USER, BD_NAME


def rm_ongs():
    print "Delete ONG directory."
    local = os.path.dirname(os.path.abspath(__file__))
    shutil.rmtree(os.path.join(local, ONG_FOLDER))


def rm_db():
    print "Remove database %s" % BD_NAME
    engine = sqlalchemy.create_engine('mysql://%s:%s@%s' % (BD_USER, BD_PASSWORD, BD_HOST))
    engine.execute("DROP DATABASE `%s`" % BD_NAME)