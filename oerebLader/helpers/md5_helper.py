# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import tempfile
import os
import requests
import zipfile

def get_md5_from_zip(zip_url):
    #~ Temporaeren Dateinamen bilden
    tempDir = tempfile.mkdtemp()
    tempFile = os.path.join(tempDir, "data.zip")

    # aus: http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    r = requests.get(zip_url, stream=True)
    with open(tempFile, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    if zipfile.is_zipfile(tempFile):
        zip_file = zipfile.ZipFile(tempFile, "r")
        for name in zip_file.namelist():
            if name.endswith(".md5.txt"):
                md5_new = zip_file.read(name)
        zip_file.close()
    
    os.remove(tempFile)
    
    return md5_new