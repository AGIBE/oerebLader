# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import logging
import os
import datetime
import cx_Oracle

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "refresh_statistics")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "refresh_statistics.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "refresh_statistics" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    logger.info("Das Logfile heisst: " + logfile)
    
    return logger

def execute_procedure(connection_string, proc):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.callproc()

def run_refresh_statistics():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    
    logger.info("Statistiken des ÖREB-Schemas in VEK2 werden aktualisiert.")
    with cx_Oracle.connect(config['OEREB_VEK2']['connection_string']) as conn:
        cur = conn.cursor()
        cur.callproc(name="dbms_stats.gather_schema_stats", keywordParameters={'options': 'GATHER AUTO', 'ownname':'oereb'})

    logger.info("Statistiken des ÖREB-Schemas in VEK1 werden aktualisiert.")
    with cx_Oracle.connect(config['OEREB_VEK1']['connection_string']) as conn:
        cur = conn.cursor()
        cur.callproc(name="dbms_stats.gather_schema_stats", keywordParameters={'options': 'GATHER AUTO', 'ownname':'oereb'})
    
    logger.info("Statistiken wurden aktualisiert.")