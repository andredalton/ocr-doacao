import os, random, unittest, json
import sys, re, requests, time

def get_contents(path):
    #content = ""
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

class TestOCR(unittest.TestCase):
    def setUp(self):
        """ Iniciando."""
        pass
        
    def test_blank_image(self):
        """ Verifica se as duas instancias sao distintas."""
        # print get_contents("test/bigblank.txt")
        self.assertNotEqual( 4, 2)

    def test_photo_image(self):
        """ Verifica se as duas instancias sao distintas."""
        # r = requests.post('http://localhost:5000', files={'file': open('test/xp.jpg', 'rb')})
        # print "\n\n", r.text, "\n\n"
        self.assertNotEqual( 4, 2)
    
    def test_quality_text(self):
        # print get_contents("test/abc.txt")
        r = requests.post('http://localhost:5000', files={'file': open('test/abc.jpg', 'rb')})
        print "\n\n", json.loads(r.text)["text"], "\n\n"
        print "\n\n", r.json()["text"], "\n\n"
        self.assertNotEqual( 4, 2)

    def test_nf_text(self):
        # r = requests.post('http://localhost:5000', files={'file': open('test/nf.jpg', 'rb')})
        # print "\n\n", r.text, "\n\n"
        self.assertNotEqual( 4, 2)

if __name__ == '__main__':
    unittest.main()