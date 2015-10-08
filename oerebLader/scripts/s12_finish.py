# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging

def run(config):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # ArcGIS Connection-Files löschen
    logging.info("Lösche Connectionfile " + config['GEODB_WORK']['connection_file'])
    os.remove(config['GEODB_WORK']['connection_file'])
    logging.info("Lösche Connectionfile " + config['OEREB_WORK']['connection_file'])
    os.remove(config['OEREB_WORK']['connection_file'])
    
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")