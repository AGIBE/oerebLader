# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import requests
import sys
import oerebLader.logging
import oerebLader.config

def run_download_tickets():

    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("download_tickets", config)

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
    
    
    