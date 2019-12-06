# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import sys
import fmeobjects
import arcpy
import tempfile
import datetime
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.fme_helper


def init_logging(config):
    log_directory = os.path.join(
        config['LOGGING']['basedir'], "update_municipality"
    )
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "update_municipality.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "update_municipality" + datetime.datetime.now(
        ).strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)

    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(
        oerebLader.helpers.log_helper.create_loghandler_file(logfile)
    )
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False

    return logger


def create_connection_files(username, password, database):

    temp_directory = tempfile.mkdtemp()
    sde_filename = "vek1.sde"
    connection_file = os.path.join(temp_directory, sde_filename)
    arcpy.CreateDatabaseConnection_management(
        temp_directory, sde_filename, "ORACLE", database, "DATABASE_AUTH",
        username, password
    )
    return connection_file


def run_update_municipality(source, target):

    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)

    logger.info("Municipality-Tabelle wird aktualisiert.")

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_script_logfile = os.path.splitext(__file__)[0] + "_fme.fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(
        fme_script_logfile, config['LOGGING']['log_directory']
    )
    logger.info("Script " + fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()

    source_tablename = "GEODB." + source
    logger.info("Quelle der Aktualisierung: %s" % source_tablename)

    target_keyname = "OEREB_%s_PG" % (target.upper())
    logger.info("Ziel der Aktualisierung: %s" % target)

    source_connectionfile = create_connection_files(
        config['GEO_VEK1']['username'], config['GEO_VEK1']['password'],
        config['GEO_VEK1']['database']
    )
    logger.info("VEK1-Connectionfile angelegt in %s" % source_connectionfile)

    logo_base_path = config['GENERAL']['files_be_ch_baseurl'] + "/logos/"
    logger.info("Basispfad Logos %s" % logo_base_path)

    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'OEREB_PG_DB': str(config[target_keyname]['database']),
        'OEREB_PG_USERNAME': str(config[target_keyname]['username']),
        'OEREB_PG_PASSWORD': str(config[target_keyname]['password']),
        'OEREB_PG_HOST': str(config[target_keyname]['host']),
        'OEREB_PG_PORT': str(config[target_keyname]['port']),
        'SOURCETABLE': str(source_tablename),
        'VEK1_CONNECTIONFILE': str(source_connectionfile),
        'LOGO_BASE_PATH': str(logo_base_path),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error(
            "FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!"
        )
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()

    logger.info("Connection-File wird gelöscht.")
    if os.path.exists(source_connectionfile):
        os.remove(source_connectionfile)
