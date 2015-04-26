import os
import shutil

from __init__ import ONG_FOLDER

origin = os.path.dirname(os.path.abspath(__file__))
destiny = os.getcwd()

print "Create ONG directory."
os.mkdir(os.path.join(destiny, ONG_FOLDER))

templateo = os.path.join(origin, "templates")
templated = os.path.join(destiny, "templates")
print "Create template directory."
shutil.copytree(templateo, templated)

# Resta criar o banco de dados.