# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.logging
import os
import datetime
import urllib2
import sys

def run_refresh_verschnitt():
    config = oerebLader.helpers.config.get_config()
    logger = oerebLader.logging.init_logging("refresh_verschnitt", config)
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