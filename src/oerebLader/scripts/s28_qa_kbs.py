# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import sys
import arcpy

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    toolbox = config['GENERAL']['qa_toolbox']
    logger.info("Folgende Toolbox wird verwendet: " + toolbox)
    arcpy.AddToolbox(toolbox)             
                           
    qa_spec = os.path.join(config['GENERAL']['qa'], "BALISKBS.qa.xml")
    logger.info("Die folgende QA-Spez wird verwendet: " + qa_spec)
    
    result_dir_name = unicode("qa_BALISKBS_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    result_dir = os.path.join(config['LOGGING']['log_directory'], result_dir_name)
    logger.info("Die Resultate werden ausgegeben in: " + result_dir)
    
    result = arcpy.XmlBasedVerificationTool_ProSuite(qa_spec,"BALISKBS","25000","GEODB " + config['GEODB_WORK']['connection_file'], "No", result_dir, "File Geodatabase")
    if unicode(result.getOutput(1))== "true":
        logger.info("QA-Check Geoprodukt BALISKBS ohne Fehler durchgelaufen.")
    else:
        logger.error("QA-Check Geoprodukt BALISKBS mit Fehlern abgeschlossen.")
        logger.error("Import wird abgebrochen.")
        sys.exit()