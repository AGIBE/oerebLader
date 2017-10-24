# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import logging
import shutil
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "collect_legends")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "collect_legends.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "build_map" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_collect_legends():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Die aktuellen Gemeinde-Legenden werden zusammengesucht.")
    
    legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], "legenden/gemeinden")

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
    
    legends_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], legenden_sql)
    
    for legend in legends_result:
        source_legend_de = legend[2].replace(config['GENERAL']['files_be_ch_baseurl'], config['GENERAL']['files_be_ch_baseunc'])
        source_legend_de = source_legend_de.replace("npl", "komplett")
        source_legend_fr = legend[3].replace(config['GENERAL']['files_be_ch_baseurl'], config['GENERAL']['files_be_ch_baseunc'])
        source_legend_fr = source_legend_fr.replace("npl", "komplett")
        
        bfsnr = unicode(legend[1])
        
        target_legendname_de = bfsnr + "_de.html"
        target_legendname_fr = bfsnr + "_fr.html"
        
        target_legende_de = os.path.join(legend_dir, target_legendname_de)
        target_legende_fr = os.path.join(legend_dir, target_legendname_fr)
        
        logger.info("Kopiere " + source_legend_de)
        logger.info("nach " + target_legende_de)
        shutil.copy2(source_legend_de, target_legende_de)
        logger.info("Kopiere " + source_legend_fr)
        logger.info("nach " + target_legende_fr)
        shutil.copy2(source_legend_fr, target_legende_fr)
    
    