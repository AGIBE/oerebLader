# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import codecs
import datetime
import logging
import mappyfile
import oerebLader.helpers.log_helper
import oerebLader.helpers.mapfile_helper

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "build_mapfile_kanton")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "build_mapfile_kanton.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "build_mapfile_kanton" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_build_mapfile_kantonr():
    mode = "oerebpruef_kanton"
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Das Mapfile für den Kantons-Prüfdienst wird neuerstellt.")
    
    repo_dir = os.environ["OEREB_REPO_PRUEF"]
    template_mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef.map")
    
    kanton_mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef_kanton.map")
    
    logger.info("Template Mapfile wird gelesen: " + template_mapfile_path)
    with codecs.open(template_mapfile_path, "r", "utf-8") as template_mapfile:
        template_mapfile_content = template_mapfile.read()
    
    logger.info("Strings werden ersetzt.")
    template_mapfile_content = template_mapfile_content.replace("[[[BFSNR]]]","")
    
    logger.info("Mapfile des Kantons-Prüfdienst wird geschrieben.")
    with codecs.open(kanton_mapfile_path, "w", "utf-8") as kanton_mapfile:
        kanton_mapfile.write(template_mapfile_content)

    logger.info("Mapfile des Kantons-Prüfdienst wird mit mappyfile geparst: " + kanton_mapfile_path)
    mf_content = mappyfile.load(kanton_mapfile_path)
    
    # Sprachunabhängige Parameter manipulieren
    
    # Stufe MAP
    mf_content = oerebLader.helpers.mapfile_helper.fill_map_metadata(mf_content, mode, config)
    
    # Stufe LAYER
    mf_content = oerebLader.helpers.mapfile_helper.fill_layer_metadata(mf_content, mode, config)
        
    # Sprachabhängige Parameter manipulieren

    # Stufe MAP
    mf_content = oerebLader.helpers.mapfile_helper.fill_map_language_metadata(mf_content, "de", mode, config)
    
    # Stufe LAYER
    mf_content = oerebLader.helpers.mapfile_helper.fill_layer_language_metadata(mf_content, "de", config)
    
    logger.info("Mapfile des Kantons-Prüfdienst wird geschrieben.")
    with codecs.open(kanton_mapfile_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(mappyfile.dumps(mf_content))        
    
    logger.info("Mapfile des Kantons-Prüfdienst wurde neuerstellt.")
