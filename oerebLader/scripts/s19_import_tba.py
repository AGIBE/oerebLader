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
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    tba_path = config['LIEFEREINHEIT']['ts_source']
    excel_amt_filename = "AMT_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx"
    excel_amt_file = os.path.join(tba_path, excel_amt_filename)
    excel_darstellungsdienst_filename = "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx"
    excel_darstellungsdienst_file = os.path.join(tba_path, excel_darstellungsdienst_filename)
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/TBA/baulinie_kantonsstrasse.png"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/TBA/baulinie_kantonsstrasse.png"

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
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'TBA_DATABASE': str(config['TBA_WORK']['database']),
        'TBA_USERNAME': str(config['TBA_WORK']['username']),
        'TBA_PASSWORD': str(config['TBA_WORK']['password']),
        'EXCEL_AMT': str(excel_amt_file),
        'EXCEL_DARSTELLUNGSDIENST': str(excel_darstellungsdienst_file),
        'LEGEND_BASEURL': str(legend_baseurl),
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
    
