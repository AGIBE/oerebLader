# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import tempfile
import os
import requests
import zipfile
import chardet
import codecs

def detect_encoding(encoded_filename):
    with open(encoded_filename, 'r') as encoded_file:
        detect_result = chardet.detect(encoded_file.read())
        detected_encoding = detect_result['encoding']
        
        return detected_encoding         

def get_md5_from_zip(zip_url):
    #~ Temporaeren Dateinamen bilden
    tempDir = tempfile.mkdtemp()
    tempFile = os.path.join(tempDir, "data.zip")
    md5_filename = ""

    # aus: http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(zip_url, stream=True, headers=headers)
    with open(tempFile, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    if zipfile.is_zipfile(tempFile):
        zip_file = zipfile.ZipFile(tempFile, "r")
        for name in zip_file.namelist():
            if name.endswith(".md5.txt"):
                md5_filename = os.path.join(tempDir, name)
                zip_file.extract(name, tempDir)
        zip_file.close()
    
    os.remove(tempFile)    
    
    md5_encoding = detect_encoding(md5_filename)
    with codecs.open(md5_filename, 'r', encoding=md5_encoding) as md5_file:
        md5_new = md5_file.read()
    
    return md5_new