# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import oerebLader.create_legend.legend

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    gemname = config['LIEFEREINHEIT']['gemeinde_name']
    logger.info("Die Legende für die Gemeinde " + unicode(bfsnr) + " wird erstellt.")

    # Legendenverzeichnis wird - wenn nötig - erstellt. 
    legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    if not os.path.exists(legend_dir):
        os.makedirs(legend_dir)
    logger.info("Die Legenden werden abgelegt in: " + legend_dir)
        
    oerebLader.create_legend.legend.create_legends(legend_dir, gemname, bfsnr, config['LIEFEREINHEIT']['id'], config['OEREB2_WORK']['connection'], config['LEGENDS']['legend_template_dir'])
    logger.info("NPL-Legenden (de/fr) und Komplette Gemeinde-Legenden (de/fr) wurden erstellt")
     
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
