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
    log_directory = os.path.join(config['LOGGING']['basedir'], "switch_bfsnr")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "switch_bfsnr.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "switch_bfsnr" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_switch_bfsnr(bfsnr):
    mode = "oerebpruef_gemeinde"
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Die BFS-Nummer im Gemeinde-Prüfdienst wird gewechselt auf: " + unicode(bfsnr))
    
    repo_dir = os.environ["OEREB_REPO_PRUEF"]
    layers = []
    for layer in config['KOMMUNALE_LAYER']:
        layers.append(layer['layer'].split(".")[1])

    search_string = "[[[BFSNR]]]"
    bfsnr = unicode(bfsnr)
    template_mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef.map")
    
    filter_string = " and bfsnr=" + bfsnr
    
    mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef_gemeinde.map")

    logger.info("Template Mapfile öffnen: " + template_mapfile_path)
    with codecs.open(template_mapfile_path, "r", encoding="utf-8") as template_mapfile:
        template_content = template_mapfile.read()
    
    logger.info("Filter-String ersetzen mit: " + filter_string)
    template_content = template_content.replace(search_string, filter_string)
    
    for layer in layers:
        layer_search_string = "###" + layer + "###"
        layer_replace_string = 'INCLUDE "nupla/' + bfsnr + '/' + layer + '_' + bfsnr + '.map"'
        logger.info("Layer-String ersetzen: " + layer_replace_string)
        template_content = template_content.replace(layer_search_string, layer_replace_string)
    
    logger.info("Gemeinde-Mapfile schreiben: " + mapfile_path)
    with codecs.open(mapfile_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(template_content)
        
    logger.info("Gemeinde-Mapfile wird mit mappyfile geparst: " + mapfile_path)
    mf_content = mappyfile.load(mapfile_path)
    
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
    
    logger.info("Gemeinde-Mapfile schreiben: " + mapfile_path)
    with codecs.open(mapfile_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(mappyfile.dumps(mf_content))
        
    logger.info("BFS-Nummer im Gemeinde-Prüfdienst wurde gewechselt auf: " + bfsnr)