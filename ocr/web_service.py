#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

from werkzeug.serving import run_simple
from flask import Flask, render_template, request
from flask.ext.classy import FlaskView, route

from persistence import Session
from persistence.ong import Ong
from persistence.image import Image
from . import HOST, ALLOWED_EXTENSIONS, ONG_FOLDER


class OcrWebView(FlaskView):
    route_base = HOST
    def __init__(self, debug=False, host='0.0.0.0', port=5000):
        self.app = Flask(__name__, static_folder=ONG_FOLDER, static_url_path=os.path.join(HOST, ONG_FOLDER))
        self.host = host
        self.port = port
        self.debug = debug
        self.session = Session()

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @route('<ong>', methods=['GET', 'POST'])
    def upload_file(self, ong=None):
        o = Ong(session=self.session.get_session(), name=ong)
        print o.load()
        if not o.load():
            return render_template("404.html"), 404
        if request.method == 'POST':
            fd = request.files['file']
            if fd and self.allowed_file(fd.filename):
                i = Image(session=self.session.get_session(), fd=fd, ong_name=ong)
                if i.save():
                    return render_template('response.html', msg="Imagem salva corretamente.", ong=o.get_name())
                else:
                    return render_template('response.html',msg="Falha ao salvar imagem.", ong=o.get_name())
        return render_template('ong.html', completeName=o.get_complete_name(), ong=o.get_name(), image=o.get_image(),
                               homepage=o.get_homepage(), css=o.get_css())

    def start(self):
        self.register(self.app)
        run_simple('localhost', 5000, self.app,
                   use_reloader=True, use_debugger=True, use_evalex=True)
        # self.app.run(host=self.host, port=self.port, debug=self.debug)