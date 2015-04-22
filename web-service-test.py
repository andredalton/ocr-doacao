#!/usr/bin/python
# -*- coding: UTF8 -*-

import os
import unittest
import time

import requests

from subprocess import Popen

from config import HOST
from functions import port, file_get_contents, free_port


def get_contents(imagename):
    """
    A funcao pega o conteudo de um arquivo de gabarito
    e compara com a resposta do webservice.
    """
    (name, ext) = os.path.splitext(imagename)
    txtname = name + ".txt"
    txtcontent = file_get_contents(txtname)
    r = requests.post('http://localhost:' + port() + HOST, files={'file': open(imagename, 'rb')})
    imagecontent = r.json()["text"]
    return txtcontent, imagecontent


class TestOCR(unittest.TestCase):
    def setUp(self):
        """ Iniciando."""
        self.port = port()
        if self.port == 0:
            print "Aqui"
            self.port = free_port()
            self.process = Popen(["python web-service.py -p %d" % self.port])
            time.sleep(10)
        self.host = 'http://localhost:5000'

    def tearDown(self):
        self.process.terminate()
        self.process.wait()

    def test_blank_image(self):
        """ Verifica se as duas instancias sao distintas."""
        (txt, image) = get_contents('test/bigblank.jpg')
        self.assertEqual("".join(txt.split()), "".join(image.split()))

    def test_nf_text(self):
        (txt, image) = get_contents('test/nf.jpg')
        self.assertEqual("".join(txt.split()), "".join(image.split()))

    def test_photo_image(self):
        """ Verifica se as duas instancias sao distintas."""
        (txt, image) = get_contents('test/xp.jpg')
        self.assertEqual("".join(txt.split()), "".join(image.split()))

    def test_quality_text(self):
        (txt, image) = get_contents('test/abc.jpg')
        self.assertEqual("".join(txt.split()), "".join(image.split()))


if __name__ == '__main__':
    unittest.main()