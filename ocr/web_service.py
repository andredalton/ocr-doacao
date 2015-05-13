#!/usr/bin/python
# -*- coding: UTF8 -*-

import os

from flask import Flask, render_template, request, jsonify, send_file, redirect
from flask.ext.classy import FlaskView, route

from persistence import Session
from persistence.ong import Ong
from persistence.image import Image
from persistence.meta_image import MetaImage
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

    @route('static/<path:path>')
    def static_file(self, path):
        if path.split("/")[0] not in ["images", "css", "js"]:
            return redirect(HOST + '/error')
        try:
            return send_file(path)
        except IOError:
            return redirect(HOST + '/error')

    @route('<ong>', methods=['GET', 'POST'])
    @route('<ong>/', methods=['GET', 'POST'])
    def upload_file(self, ong=None):
        o = Ong(session=self.session.get_session(), name=ong)
        if not o.load():
            return redirect(HOST + '/error')
        if request.method == 'POST':
            fd = request.files['file1']
            if fd and self.allowed_file(fd.filename):
                i = Image(session=self.session.get_session(), fd=fd, ong_name=ong)
                if i.save():
                    return render_template('response.html', msg="Imagem salva corretamente.", ong=o.get_name())
                else:
                    return render_template('response.html', msg="Falha ao salvar imagem.", ong=o.get_name())
        return render_template('ong.html', host=HOST)

    @route('<ong>/cadastro', methods=['GET', 'POST'])
    def cadastre(self, ong):
        o = Ong(session=self.session.get_session(), name=ong)
        if not o.load():
            return redirect(HOST + '/error')
        if request.method == 'POST':
            cnpj = request.form["cnpj"]
            coo = request.form["coo"]
            data = request.form["data"]
            total = request.form["total"]
            id_image = request.form["id_image"]
            meta = MetaImage(session=self.session.get_session(), id_image=id_image)
            meta.load()
            meta.cnpj = cnpj
            meta.coo = coo
            meta.data = data
            meta.total = total
            meta.status = "valid"
            meta.update()
            return redirect(os.path.join(HOST, o.get_name(), 'cadastro'))
        meta = MetaImage(session=self.session.get_session(), id_ong=o.get_id())
        meta.search()
        if meta.id_image is None:
            return render_template('response.html', msg="Todas as imagens foram cadastradas!", ong=o.get_name(), host=HOST)
        i = Image(session=self.session.get_session(), id=meta.id_image)
        return render_template('cadastre.html', meta=meta, ong=o.get_name(), img=i, host=HOST)

    @route('<ong>/list')
    def list_images(self, ong=None):
        o = Ong(session=self.session.get_session(), name=ong)
        if not o.load():
            return redirect(HOST + '/error')
        i = Image(session=self.session.get_session(), ong_name=ong)
        lst = i.search()
        return jsonify({'images': lst})

    @route('<ong>/<path:path>')
    def get_ong_file(self, ong, path):
        return send_file(os.path.join(ONG_FOLDER, ong, path))

    def start(self):
        self.register(self.app)
        self.app.run(host=self.host, port=self.port, debug=self.debug)
