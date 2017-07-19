# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import sys
import arcpy
import oerebLader.create_qaspecs.create_qaspecs

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    toolbox = config['GENERAL']['qa_toolbox']
    logger.info("Folgende Toolbox wird verwendet: " + toolbox)
    arcpy.AddToolbox(toolbox)
    
    logger.info("Die QA-Spez wird neu erstellt.")
    liefereinheiten = [config['LIEFEREINHEIT']['id']]
    oerebLader.create_qaspecs.create_qaspecs.run_create_qaspecs(config, liefereinheiten)
                           
    qa2_spec = os.path.join(config['GENERAL']['qa'], "OEREB2", "OEREB2_" + unicode(config['LIEFEREINHEIT']['id']) + ".qa.xml")
    logger.info("Die folgenden QA-Spez werden verwendet: " + qa2_spec)
    
    result2_dir_name = unicode("qa_OEREB2_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    result2_dir = os.path.join(config['LOGGING']['log_directory'], result2_dir_name)
    logger.info("Die Resultate werden ausgegeben in: " + result2_dir)
            
    result2 = arcpy.XmlBasedVerificationTool(qa2_spec,"OEREB2","25000","OEREBK2-Transferstrukturchecker " + config['OEREB2_WORK']['connection_file'], "No", result2_dir, "File Geodatabase")
    if unicode(result2.getOutput(1))== "true":
        logger.info("QA-Check Transferstruktur 2 ohne Fehler durchgelaufen.")
    else:
        logger.error("QA-Check Transferstruktur 2 mit Fehlern abgeschlossen.")
        logger.error("Import wird abgebrochen.")
        sys.exit()
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")