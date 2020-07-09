# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import logging
import shutil
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "collect_legends")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "collect_legends.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "collect_legends" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

# aus: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
    retries=5,
    backoff_factor=2,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_file(url, file_path, logger):
    # Aufruf mit Retry und Backoff
    # umgeht Schwierigkeiten mit SSLError
    # "Max retries exceeded with url..."
    r = requests_retry_session().get(url)
    if r.status_code == 200:
        with open(file_path, 'w') as f:
            f.write(r.content)
    else:
        logger.warn("File konnte nicht heruntergeladen werden.")
        logger.warn(r.status_code)
        

def copy_legends(mode, config, logger):

    if mode=='oereb':
        legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], "legenden/gemeinden/oereb")
        connection = config['OEREB2_VEK1']['connection_string']
    if mode=='oerebpruef':
        legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], "legenden/gemeinden/oerebpruef")
        connection = config['OEREB2_WORK']['connection_string']

    logger.info("Das Legenden-Verzeichnis lautet: " + legend_dir)
    if not os.path.exists(legend_dir):
        logger.info("Das Legenden-Verzeichnis existiert nicht. Es wird neu angelegt.")
        os.makedirs(legend_dir)
    
    logger.info("Das Legenden-Verzeichnis wird geleert.")
    for file_in_dir in os.listdir(legend_dir):
        file_path = os.path.join(legend_dir, file_in_dir)
        if os.path.isfile(file_path) and os.path.splitext(file_path)[1] == '.html':
            logger.info("lösche " + file_path)
            os.remove(file_path)
    
    legenden_sql = "select distinct dar_liefereinheit, substr(dar_liefereinheit, 0, 3) bfsnr, DAR_LEGENDEIMWEB_DE, DAR_LEGENDEIMWEB_FR from oereb2.darstellungsdienst where dar_liefereinheit like '___01' and dar_legendeimweb_de like '%.html'"
    legends_result = oerebLader.helpers.sql_helper.readSQL(connection, legenden_sql)
    
    for legend in legends_result:
        
        source_legend_de = legend[2].replace("npl", "komplett")
        source_legend_fr = legend[3].replace("npl", "komplett")
        
        bfsnr = unicode(legend[1])
        target_legendname_de = os.path.join(legend_dir, bfsnr + "_de.html")
        target_legendname_fr = os.path.join(legend_dir, bfsnr + "_fr.html")
        
        logger.info("Lade herunter: " + source_legend_de)
        logger.info("Kopiere nach: " + target_legendname_de)
        download_file(source_legend_de, target_legendname_de, logger)

        logger.info("Lade herunter: " + source_legend_fr)
        logger.info("Kopiere nach: " + target_legendname_fr)
        download_file(source_legend_fr, target_legendname_fr, logger)
        

def run_collect_legends():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    
    logger.info("Legenden der öffentlichen Karte werden kopiert.")
    copy_legends("oereb", config, logger)
    
    logger.info("Legenden der Prüfkarte werden kopiert.")
    copy_legends("oerebpruef", config, logger)

    

    
    