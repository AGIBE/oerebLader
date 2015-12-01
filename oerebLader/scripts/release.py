# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.log_helper
import os
import datetime
import logging
import chromalog

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "release") 
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "release_" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log")
    
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger


def run_release():
    config = oerebLader.helpers.config.get_config()
    
    logger = init_logging(config)
    
    logger.info("Das Release wird initialisiert!")