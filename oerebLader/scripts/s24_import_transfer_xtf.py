# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os

def run(config):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")