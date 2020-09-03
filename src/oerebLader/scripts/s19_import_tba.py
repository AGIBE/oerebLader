# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw",".log")) 
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    tba_path = config['LIEFEREINHEIT']['ts_source']
    excel_amt_file = config['GENERAL']['amt_tabelle']
    excel_darstellungsdienst_filename = "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx"
    excel_darstellungsdienst_file = os.path.join(tba_path, excel_darstellungsdienst_filename)
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_fullurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/TBA/baulinie_kantonsstrasse.png"
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/TBA/"
    else:
        legend_fullurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/TBA/baulinie_kantonsstrasse.png"
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/TBA/"

    parameters = {
        'EXCEL_AMT': excel_amt_file,
        'EXCEL_DARSTELLUNGSDIENST': excel_darstellungsdienst_file,
        'LIEFEREINHEIT': unicode(config['LIEFEREINHEIT']['id']),
        'STROKER': unicode(config['GENERAL']['fme_stroker_value']),
        'GEODB_DATABASE': config['GEODB_WORK']['database'],
        'GEODB_USERNAME': config['GEODB_WORK']['username'],
        'GEODB_PASSWORD': config['GEODB_WORK']['password'],
        'TBA_DATABASE': config['TBA_WORK']['database'],
        'TBA_USERNAME': config['TBA_WORK']['username'],
        'TBA_PASSWORD': config['TBA_WORK']['password'],
        'OEREB2_DATABASE': config['OEREB2_WORK']['database'],
        'OEREB2_USERNAME': config['OEREB2_WORK']['username'],
        'OEREB2_PASSWORD': config['OEREB2_WORK']['password'],
        'LEGEND_FULLURL': legend_fullurl,
        'LEGEND_BASEURL': legend_baseurl,
        'GEODB_PG_DATABASE': config['GEODB_WORK_PG']['database'],
        'GEODB_PG_USERNAME': config['GEODB_WORK_PG']['username'],
        'GEODB_PG_PASSWORD': config['GEODB_WORK_PG']['password'],
        'GEODB_PG_HOST': config['GEODB_WORK_PG']['host'],
        'GEODB_PG_PORT': unicode(config['GEODB_WORK_PG']['port']),
        'OEREB_PG_DATABASE': config['OEREB_WORK_PG']['database'],
        'OEREB_PG_USERNAME': config['OEREB_WORK_PG']['username'],
        'OEREB_PG_PASSWORD': config['OEREB_WORK_PG']['password'],
        'OEREB_PG_HOST': config['OEREB_WORK_PG']['host'],
        'OEREB_PG_PORT': unicode(config['OEREB_WORK_PG']['port'])
    }

    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
