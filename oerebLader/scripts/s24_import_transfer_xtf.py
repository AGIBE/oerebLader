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
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], "legenden", unicode(config['LIEFEREINHEIT']['id']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/" + unicode(config['LIEFEREINHEIT']['id']) + "/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/" + unicode(config['LIEFEREINHEIT']['id']) + "/"

    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'MODELLABLAGE': str(config['GENERAL']['models']),
        'XTF_FILE': str(config['LIEFEREINHEIT']['ts_source']),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LEGEND_BASEDIR': str(legend_basedir),
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