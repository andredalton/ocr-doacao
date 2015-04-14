#coding: utf-8

import os, json, sys, re, socket, argparse
from subprocess import call, check_output
from flask import Flask, request, send_from_directory
from werkzeug import secure_filename
from ocr_config import HOST, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DAEMON, DEBUG, free_port
from ocr import call_tesseract

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
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route(HOST+"/<ong>", methods=['GET', 'POST'])
def upload_file(ong):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            completename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(completename)
            out = call_tesseract(completename)
            data = {'text':out}
            return json.dumps(data)

    return '''
    <!doctype html>
    <title>Envio de Imagem</title>
    <center>
    <h1> %s </h1>
    <h2>Envie uma Imagem</h2>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    </center>
    ''' % ong


@app.route(HOST+'/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='WebService for OCR.')
    parser.add_argument('-H','--host', metavar='IP', nargs='?', type=valid_ip, help='Host ip', default='0.0.0.0')
    parser.add_argument('-p','--port', metavar='PORT', nargs='?', type=valid_port, help='Port number', default=5000)
    args = parser.parse_args()

    if args.port == 0:
        args.port = free_port()

    f = os.open(DAEMON, os.O_WRONLY|os.O_CREAT)
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