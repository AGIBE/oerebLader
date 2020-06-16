# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import datetime
import requests
import sys
import oerebLader.helpers.log_helper
import oerebLader.helpers.config

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "download_tickets")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "download_tickets.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "download_tickets" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_download_tickets():

    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)

    logger.info("Tickets werden heruntergeladen.")

    username = config['TICKETSYSTEM']['username']
    password = config['TICKETSYSTEM']['password']

    for idx, url in enumerate(config['TICKETSYSTEM']['download_urls']):
        output_file = config['TICKETSYSTEM']['download_files'][idx]
        logger.info("Lade herunter...")
        logger.info(url)
        
        r = requests.get(url, auth=(username, password))

        if r.status_code == 200:
            with open(output_file, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            logger.error("File konnte nicht heruntergeladen werden.")
            logger.error("Script wird abgebrochen.")
            sys.exit()
    
    
    