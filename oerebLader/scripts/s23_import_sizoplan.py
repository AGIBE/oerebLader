# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects

def run(config):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logging.info("Script " +  fme_script + " wird ausgeführt.")
    logging.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'DATABASE': str(config['GEODB_WORK']['database']),
        'USERNAME': str(config['GEODB_WORK']['username']),
        'PASSWORD': str(config['GEODB_WORK']['password']),
        'MODELLABLAGE': str(config['GENERAL']['models']),
        'XTF_FILE': str(config['LIEFEREINHEIT']['gpr_source']),
        'GPRCODE': str(config['LIEFEREINHEIT']['gprcode']),
        'LOGFILE': str(fme_logfile)
    }
    logging.info(unicode(parameters))
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logging.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logging.error(ex)
        logging.error("Import wird abgebrochen!")
        sys.exit()
        
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")