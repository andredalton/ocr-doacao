import argparse

from ocr.persistence.ong import Ong
from ocr.persistence import Session


def main():
    parser = argparse.ArgumentParser(description='Delete ong in the system.')
    parser.add_argument('name', help='Name of ong')
    args = parser.parse_args()
    name = args.name

    session = Session()
    o = Ong(session=session.get_session(), name=name)
    o.delete()

if __name__ == "__main__":
    main()