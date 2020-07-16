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
    logger.info("Script " +  fme_script + " wird ausgef�hrt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    excel_file_amt = config['GENERAL']['amt_tabelle']
    excel_file_darstellungsdienst = os.path.join(config['LIEFEREINHEIT']['ts_source'], "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/KBS/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/KBS/"
    
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'GEODB_DATABASE': str(config['GEODB_WORK']['database']),
        'GEODB_USERNAME': str(config['GEODB_WORK']['username']),
        'GEODB_PASSWORD': str(config['GEODB_WORK']['password']),
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'OEREB_PG_DATABASE': str(config['OEREB_WORK_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_WORK_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_WORK_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_WORK_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_WORK_PG']['port']),
        'EXCEL_DARSTELLUNGSDIENST': str(excel_file_darstellungsdienst),
        'EXCEL_AMT': str(excel_file_amt),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'RV_BASEURL': str(config['GENERAL']['kbs_call']),
        'STROKER': str(config['GENERAL']['fme_stroker_value'])
    }

    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
