from ocr.setup import is_installed, new_ong_dir, create_database, create_tables

if not is_installed():
    print "Installing..."
    new_ong_dir()
    create_database()
    create_tables()
else:
    print "Installed"