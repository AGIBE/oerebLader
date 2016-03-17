# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import logging
import os
import datetime
import urllib2
import sys

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "refresh_verschnitt")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "refresh_verschnitt.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "refresh_verschnitt" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_refresh_verschnitt():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Folgende URL werden refreshed: ")
    
    for vs_url in config['GENERAL']['verschnitt_urls']:
        dictcache_url = vs_url + config['GENERAL']['verschnitt_dictcaches']
        response = urllib2.urlopen(dictcache_url)
        if response.getcode() == 200:
            logger.info("Dicionary Caches (" + vs_url +") aktualisiert.")
        else:
            logger.error("Dicionary Caches (" + vs_url +") nicht aktualisiert.")
            sys.exit()
        
        config_url = vs_url + config['GENERAL']['verschnitt_config']
        response = urllib2.urlopen(config_url)
        if response.getcode() == 200:
            logger.info("Konfiguration (" + dictcache_url +") aktualisiert.")
        else:
            logger.info("Konfiguration (" + dictcache_url +") nicht aktualisiert.")
            sys.exit()