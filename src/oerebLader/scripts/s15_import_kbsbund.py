# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects
import requests
import tempfile
import zipfile

logger = logging.getLogger('oerebLaderLogger')

def process_zip(zip_url):
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
            if name.endswith(".xtf") and "lv95" in name:
                xtf_filename = os.path.join(tempDir, name)
                zip_file.extract(name, tempDir)
            if name.endswith("1_4.xml"):
                xml_filename = os.path.join(tempDir, name)
                zip_file.extract(name, tempDir)
        zip_file.close()
    
    files = (xtf_filename, xml_filename)
    
    return files

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das XTF- und das XML-File werden aus dem Zip-File extrahiert.")
    xtf_files = process_zip(config['LIEFEREINHEIT']['gpr_source'])
    xtf_file = xtf_files[0]
    xml_file = xtf_files[1]
    logger.info("XTF-File: " + xtf_file)
    logger.info("XML-File: " + xml_file)
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'DATABASE': str(config['GEODB_WORK']['database']),
        'USERNAME': str(config['GEODB_WORK']['username']),
        'PASSWORD': str(config['GEODB_WORK']['password']),
        'GEODB_PG_DATABASE': str(config['GEODB_WORK_PG']['database']),
        'GEODB_PG_USERNAME': str(config['GEODB_WORK_PG']['username']),
        'GEODB_PG_PASSWORD': str(config['GEODB_WORK_PG']['password']),
        'GEODB_PG_HOST': str(config['GEODB_WORK_PG']['host']),
        'GEODB_PG_PORT': str(config['GEODB_WORK_PG']['port']),
        'MODELLABLAGE': str(config['GENERAL']['models']),
        'XTF_FILE': str(xtf_file),
        'XML_FILE': str(xml_file),
        'GPRCODE': str(config['LIEFEREINHEIT']['gprcodes'][0]),
        'LOGFILE': str(fme_logfile)
    }

    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")