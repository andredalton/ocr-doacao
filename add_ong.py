import argparse

from ocr.persistence.ong import Ong
from ocr.persistence import Session


def main():
    parser = argparse.ArgumentParser(description='Add new ong in the system.')
    parser.add_argument('name', help='Name of new ong')
    parser.add_argument('-H', '--homepage', metavar='URL', nargs='?', help='URL for ong homepage', default='#')
    parser.add_argument('-N', '--completename', metavar='CNAME', nargs='?', help='Complete name of new ong')
    args = parser.parse_args()
    name = args.name

    session = Session()
    o = Ong(session=session.get_session(), name=name)
    return o.save()

if __name__ == "__main__":
    if main():
        print "ONG inserted correctly"
    else:
        print "Fail to insert ONG"
