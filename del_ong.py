import os
import shutil
import argparse

from ocr.persistence.ong import Ong
from ocr.persistence import Session
from ocr.config import ONG_FOLDER


def main():
    parser = argparse.ArgumentParser(description='Delete ong in the system.')
    parser.add_argument('name', help='Name of ong')
    args = parser.parse_args()

    local = os.getcwd()
    name = args.name

    session = Session()
    o = Ong(session=session.get_session(), name=name)
    o.delete()

    ongpath = os.path.join(local, ONG_FOLDER, name)
    try:
        shutil.rmtree(ongpath)
    except OSError:
        print "The ONG directory does not exists"
        return False

if __name__ == "__main__":
    main()