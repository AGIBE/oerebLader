# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import sys
import logging
import os

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw",".log"))
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    bfsnr = config['LIEFEREINHEIT']['bfsnr']

    parameters = {
        'OEREB2_DATABASE': config['OEREB2_WORK']['database'],
        'OEREB2_USERNAME': config['OEREB2_WORK']['username'],
        'OEREB2_PASSWORD': config['OEREB2_WORK']['password'],
        'GEODB_DATABASE': config['GEODB_WORK']['database'],
        'GEODB_USERNAME': config['GEODB_WORK']['username'],
        'GEODB_PASSWORD': config['GEODB_WORK']['password'],
        'GEODB_PG_DATABASE': config['GEODB_WORK_PG']['database'],
        'GEODB_PG_USERNAME': config['GEODB_WORK_PG']['username'],
        'GEODB_PG_PASSWORD': config['GEODB_WORK_PG']['password'],
        'GEODB_PG_HOST': config['GEODB_WORK_PG']['host'],
        'GEODB_PG_PORT': unicode(config['GEODB_WORK_PG']['port']),
        'OEREB_PG_DATABASE': config['OEREB_WORK_PG']['database'],
        'OEREB_PG_USERNAME': config['OEREB_WORK_PG']['username'],
        'OEREB_PG_PASSWORD': config['OEREB_WORK_PG']['password'],
        'OEREB_PG_HOST': config['OEREB_WORK_PG']['host'],
        'OEREB_PG_PORT': unicode(config['OEREB_WORK_PG']['port']),
        'BFSNR': unicode(bfsnr),
        'LIEFEREINHEIT': unicode(config['LIEFEREINHEIT']['id'])
    }

    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
