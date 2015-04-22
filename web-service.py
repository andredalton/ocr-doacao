#!/usr/bin/python
# -*- coding: UTF8 -*-

import os
import socket

from flask import Flask, request, render_template

from config import HOST, ALLOWED_EXTENSIONS, DAEMON, DEBUG, ONG_FOLDER
from functions import free_port
from persistence import Ong, Image, create_session


# Validadores usados para linha de comando.
def valid_port(value):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ivalue = int(value)
        result = sock.connect_ex(('127.0.0.1', ivalue))
    except (OverflowError, ValueError):
        sock.close()
        raise argparse.ArgumentTypeError("%s is not a valid port [0-65555]." % value)
    if result == 0:
        sock.close()
        raise argparse.ArgumentTypeError("The port %s is alread in use." % value)
    sock.close()
    return ivalue


def valid_ip(value):
    try:
        socket.inet_aton(value)
    except socket.error:
        raise argparse.ArgumentTypeError("%s is not a valid ip." % value)
    return value

# Aqui se inicia a mágica WEB
app = Flask(__name__, static_folder=ONG_FOLDER, static_url_path=os.path.join(HOST, ONG_FOLDER))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route(os.path.join(HOST, "<ong>"), methods=['GET', 'POST'])
def upload_file(ong):
    session = create_session()
    o = Ong(session=session, name=ong)
    if not o.load():
        return render_template("404.html"), 404
    if request.method == 'POST':
        fd = request.files['file']
        if fd and allowed_file(fd.filename):
            i = Image(session=session, fd=fd, ong_name=ong)
            if i.save():
                return render_template('response.html', msg="Imagem salva corretamente.", ong=o.get_name())
            else:
                return render_template('response.html',msg="Falha ao salvar imagem.", ong=o.get_name())
    return render_template('ong.html', completeName=o.get_complete_name(), ong=o.get_name(), image=o.get_image(),
                           homepage=o.get_homepage(), css=o.get_css())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='WebService for OCR.')
    parser.add_argument('-H', '--host', metavar='IP', nargs='?', type=valid_ip, help='Host ip', default='0.0.0.0')
    parser.add_argument('-p', '--port', metavar='PORT', nargs='?', type=valid_port, help='Port number', default=5000)
    args = parser.parse_args()

    if args.port == 0:
        args.port = free_port()

    f = os.open(DAEMON, os.O_WRONLY | os.O_CREAT)
    os.write(f, str(args.port))
    os.close(f)
    app.run(host=args.host, port=args.port, debug=DEBUG)

    try:
        os.remove(DAEMON)
    except OSError:
        if DEBUG:
            # Em caso de debug este comando roda duas vezes.
            pass
        else:
            raise OSError