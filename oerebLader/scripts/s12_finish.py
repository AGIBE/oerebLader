# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os

def run(config):
    
    # ArcGIS Connection-Files löschen
    os.remove(config['GEODB_WORK']['connection_file'])
    os.remove(config['OEREB_WORK']['connection_file'])