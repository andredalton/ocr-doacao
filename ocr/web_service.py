#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect
from flask.ext.classy import FlaskView, route

from persistence import Session
from persistence.ong import Ong
from persistence.image import Image
from .config import HOST, ALLOWED_EXTENSIONS, ONG_FOLDER


class WebView(FlaskView):
    route_base = HOST

    def __init__(self, debug=False, host='0.0.0.0', port=5000):
        self.app = Flask(__name__, static_folder=os.path.join(os.getcwd(), ONG_FOLDER),
                         static_url_path=os.path.join(HOST, ONG_FOLDER))
        self.app_config()
        self.host = host
        self.port = port
        self.debug = debug
        self.session = Session()

    def app_config(self):
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        self.app.config["CACHE_TYPE"] = "null"

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @route('error')
    def error(self):
        return render_template("404.html", host=HOST), 404

    @route('/favicon.ico')
    def favicon(self):
        path = os.path.join(self.app.root_path, 'templates', 'defaultImages')
        return send_from_directory(path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @route('static/<path:path>')
    def static_file(self, path):
        if path.split("/")[0] not in ["images", "css", "js"]:
            return redirect(HOST + '/error')
            # return render_template("404.html"), 404
        try:
            return send_file(path)
        except IOError:
            return render_template("404.html"), 404

    @route('<ong>', methods=['GET', 'POST'])
    @route('<ong>/', methods=['GET', 'POST'])
    def upload_file(self, ong=None):
        o = Ong(session=self.session.get_session(), name=ong)
        if not o.load():
            return render_template("404.html"), 404
        if request.method == 'POST':
            fd = request.files['file1']
            if fd and self.allowed_file(fd.filename):
                i = Image(session=self.session.get_session(), fd=fd, ong_name=ong)
                if i.save():
                    return render_template('response.html', msg="Imagem salva corretamente.", ong=o.get_name())
                else:
                    return render_template('response.html', msg="Falha ao salvar imagem.", ong=o.get_name())
        return render_template('ong.html', host=HOST)

    @route('<ong>/list')
    def list_images(self, ong=None):
        o = Ong(session=self.session.get_session(), name=ong)
        if not o.load():
            return render_template("404.html"), 404
        i = Image(session=self.session.get_session(), ong_name=ong)
        lst = i.search()
        print lst
        return jsonify({'images': lst})

    @route('<ong>/<path:path>')
    def get_ong_file(self, ong, path):
        return send_file(os.path.join(ONG_FOLDER, ong, path))

    def start(self):
        self.register(self.app)
        self.app.run(host=self.host, port=self.port, debug=self.debug)
