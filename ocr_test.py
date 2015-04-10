import os, random, unittest, json
import sys, re, requests, time

def get_contents(imagename):
    """
    A funcao pega o conteudo de um arquivo de gabarito
    e compara com a resposta do webservice.
    """
    (path, ext) = os.path.splitext(imagename)
    txtname = path + ".txt"
    with open(txtname, 'r') as content_file:
        txtcontent = content_file.read()
    r = requests.post('http://localhost:5000', files={'file': open(imagename, 'rb')})
    imagecontent = r.json()["text"]
    return (txtcontent, imagecontent)

class TestOCR(unittest.TestCase):
    def test_blank_image(self):
        """ Verifica se as duas instancias sao distintas."""
        (txt, image) = get_contents('test/bigblank.jpg')
        self.assertEqual( "".join(txt.split()), "".join(image.split()))
    
    def test_nf_text(self):
        (txt, image) = get_contents('test/nf.jpg')
        self.assertEqual( "".join(txt.split()), "".join(image.split()))
 
    def test_photo_image(self):
        """ Verifica se as duas instancias sao distintas."""
        (txt, image) = get_contents('test/xp.jpg')
        self.assertEqual( "".join(txt.split()), "".join(image.split()))
    
    def test_quality_text(self):
        (txt, image) = get_contents('test/abc.jpg')
        self.assertEqual( "".join(txt.split()), "".join(image.split()))

if __name__ == '__main__':
    unittest.main()