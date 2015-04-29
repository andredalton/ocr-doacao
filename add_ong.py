import os
import shutil
import argparse
import dicttoxml

from ocr.persistence.ong import Ong
from ocr.persistence import Session
from ocr.config import ONG_FOLDER, UPLOAD_FOLDER


def main():
    parser = argparse.ArgumentParser(description='Add new ong in the system.')
    # parser.add_argument('-n', '--name', metavar='NAME', nargs=1, help='Name of new ong')
    parser.add_argument('name', help='Name of new ong')
    parser.add_argument('-H', '--homepage', metavar='URL', nargs='?', help='URL for ong homepage', default='#')
    parser.add_argument('-N', '--completename', metavar='CNAME', nargs='?', help='Complete name of new ong')

    args = parser.parse_args()

    local = os.getcwd()
    name = args.name
    if args.completename is None:
        completename = name
    else:
        completename = args.completename[0]
    homepage = args.homepage[0]

    templateo = os.path.join(local, "templates", "ong")
    templated = os.path.join(local, ONG_FOLDER, name)
    try:
        shutil.copytree(templateo, templated)
        os.mkdir(os.path.join(templated, UPLOAD_FOLDER), 0744)
    except OSError:
        print "The ong directory already exists"
        return False

    dic = {'name': name, 'completename': completename, 'homepage': homepage, 'css': "default.css", 'image': "default.png"}
    xml = dicttoxml.dicttoxml(dic, custom_root='ong', attr_type=False)
    fd = os.open(os.path.join(templated, "ong.xml"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.write(fd, xml)
    os.close(fd)
    session = Session()
    o = Ong(session=session.get_session(), name=name)
    return o.save()

if __name__ == "__main__":
    if main():
        print "ONG inserted correctly"
        print "The service must be restarted for the changes to take effect"
    else:
        print "Fail to insert ONG"
