# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import os
import logging
import sys
import arcpy
import tempfile
import datetime
import oerebLader.logging
import oerebLader.config

def run_update_municipality(source, target):

    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("update_municipality", config)

    logger.info("Municipality-Tabelle wird aktualisiert.")

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw","_fme.log"))
    logger.info("Script " + fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)

    source_tablename = "GEODB." + source
    logger.info("Quelle der Aktualisierung: %s" % source_tablename)

    target_keyname = "OEREB_%s_PG" % (target.upper())
    logger.info("Ziel der Aktualisierung: %s" % target)

    source_connectionfile = config['GEO_VEK1']['connection'].create_sde_connection()
    logger.info("VEK1-Connectionfile angelegt in %s" % source_connectionfile)

    logo_base_path = config['GENERAL']['files_be_ch_baseurl'] + "/logos/"
    logger.info("Basispfad Logos %s" % logo_base_path)

    parameters = {
        'OEREB_PG_DB': config[target_keyname]['database'],
        'OEREB_PG_USERNAME': config[target_keyname]['username'],
        'OEREB_PG_PASSWORD': config[target_keyname]['password'],
        'OEREB_PG_HOST': config[target_keyname]['host'],
        'OEREB_PG_PORT': unicode(config[target_keyname]['port']),
        'SOURCETABLE': source_tablename,
        'VEK1_CONNECTIONFILE': source_connectionfile,
        'LOGO_BASE_PATH': logo_base_path
    }
    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.info("Connection-File wird gelöscht.")
        config['GEO_VEK1']['connection'].delete_all_sde_connections()
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
    else:
        logger.info("Connection-File wird gelöscht.")
        config['GEO_VEK1']['connection'].delete_all_sde_connections()