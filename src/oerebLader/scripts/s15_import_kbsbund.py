# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import sys
import logging
import os
import fmeobjects
import requests
import tempfile
import zipfile

logger = logging.getLogger('oerebLaderLogger')

def process_zip(zip_url, liefereinheit):
    #~ Temporaeren Dateinamen bilden
    tempDir = tempfile.mkdtemp()
    tempFile = os.path.join(tempDir, "data.zip")

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
            if (name.endswith(".xtf") and "lv95" in name) or (liefereinheit=="1117" and name.endswith(".xtf")):
                xtf_filename = os.path.join(tempDir, name)
                zip_file.extract(name, tempDir)
            if name.endswith("1_4.xml"):
                xml_filename = os.path.join(tempDir, name)
                zip_file.extract(name, tempDir)
        zip_file.close()
    
    files = (unicode(xtf_filename), unicode(xml_filename))
    
    return files

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw",".log")) 
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das XTF- und das XML-File werden aus dem Zip-File extrahiert.")
    xtf_files = process_zip(config['LIEFEREINHEIT']['gpr_source'], unicode(config['LIEFEREINHEIT']['id']))
    xtf_file = xtf_files[0]
    xml_file = xtf_files[1]
    logger.info("XTF-File: " + xtf_file)
    logger.info("XML-File: " + xml_file)
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    parameters = {
        'DATABASE': config['GEODB_WORK']['database'],
        'USERNAME': config['GEODB_WORK']['username'],
        'PASSWORD': config['GEODB_WORK']['password'],
        'GEODB_PG_DATABASE': config['GEODB_WORK_PG']['database'],
        'GEODB_PG_USERNAME': config['GEODB_WORK_PG']['username'],
        'GEODB_PG_PASSWORD': config['GEODB_WORK_PG']['password'],
        'GEODB_PG_HOST': config['GEODB_WORK_PG']['host'],
        'GEODB_PG_PORT': unicode(config['GEODB_WORK_PG']['port']),
        'MODELLABLAGE': config['GENERAL']['models'],
        'XTF_FILE': xtf_file,
        'XML_FILE': xml_file,
        'GPRCODE': config['LIEFEREINHEIT']['gprcodes'][0]
    }

    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")