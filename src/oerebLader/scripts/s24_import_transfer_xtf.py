# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.fme
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.splitext(__file__)[0] + ".log")
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], "legenden", unicode(config['LIEFEREINHEIT']['id']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/" + unicode(config['LIEFEREINHEIT']['id']) + "/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/" + unicode(config['LIEFEREINHEIT']['id']) + "/"
    # Bei den Bundesthemen ist immer nur genau ein Schema betroffen.
    schema = config['LIEFEREINHEIT']['schemas'][0]

    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'OEREB2_CONNECTIONFILE': str(config['OEREB2_WORK']['connection_file']),
        'MODELLABLAGE': str(config['GENERAL']['models']),
        'XTF_FILE': str(config['LIEFEREINHEIT']['ts_source']),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LEGEND_BASEDIR': str(legend_basedir),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'OEREB_PG_DATABASE': str(config['OEREB_WORK_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_WORK_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_WORK_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_WORK_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_WORK_PG']['port']),
        'SCHEMA': str(schema),
        'STROKER': str(config['GENERAL']['fme_stroker_value'])
    }

    fmerunner = AGILib.fme.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")