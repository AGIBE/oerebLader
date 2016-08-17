# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import datetime
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "create_legend")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "create_qaspecs.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "create_qaspecs" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    logger.info("Das Logfile heisst: " + logfile)
    
    return logger

def run_create_legend(bfsnr, config=None):
    if config is not None:
        logger = logging.getLogger('oerebLaderLogger')
    else:
        config = oerebLader.helpers.config.get_config()
        logger = init_logging(config)
    
    logger.info("Die Legende für die Gemeinde " + unicode(bfsnr) + " wird erstellt.")
    
    
