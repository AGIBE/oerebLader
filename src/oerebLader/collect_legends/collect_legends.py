# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import shutil
import oerebLader.logging
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
    logger = oerebLader.logging.init_logging("collect_legends", config)
    
    logger.info("Legenden der öffentlichen Karte werden kopiert.")
    copy_legends("oereb", config, logger)
    
    logger.info("Legenden der Prüfkarte werden kopiert.")
    copy_legends("oerebpruef", config, logger)

    

    
    