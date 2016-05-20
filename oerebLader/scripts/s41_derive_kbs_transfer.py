# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgef�hrt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    excel_file_amt = os.path.join(config['LIEFEREINHEIT']['ts_source'], "AMT_1116.xlsx")
    excel_file_darstellungsdienst = os.path.join(config['LIEFEREINHEIT']['ts_source'], "DARSTELLUNGSDIENST_1116.xlsx")
    runner = fmeobjects.FMEWorkspaceRunner()
    
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'GEODB_DATABASE': str(config['GEODB_WORK']['database']),
        'GEODB_USERNAME': str(config['GEODB_WORK']['username']),
        'GEODB_PASSWORD': str(config['GEODB_WORK']['password']),
        'OEREB_DATABASE': str(config['OEREB_WORK']['database']),
        'OEREB_USERNAME': str(config['OEREB_WORK']['username']),
        'OEREB_PASSWORD': str(config['OEREB_WORK']['password']),
        'EXCEL_DARSTELLUNGSDIENST': str(excel_file_darstellungsdienst),
        'EXCEL_AMT': str(excel_file_amt),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
