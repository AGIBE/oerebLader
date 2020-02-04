# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import logging
import os
import datetime
import cx_Oracle
import psycopg2


def init_logging(config):
    log_directory = os.path.join(
        config['LOGGING']['basedir'], "refresh_statistics"
    )
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "refresh_statistics.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "refresh_statistics" + datetime.datetime.now(
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
    logger.info("Das Logfile heisst: " + logfile)

    return logger


def refresh_stats_pg(connection_string):
    with psycopg2.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("VACUUM ANALYZE")


def refresh_stats(connection_string, ownername):
    with cx_Oracle.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.callproc(
            name="dbms_stats.gather_schema_stats",
            keywordParameters={
                'options': 'GATHER AUTO',
                'ownname': ownername
            }
        )


def run_refresh_statistics():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)

    logger.info("Statistiken des ÖREB2-Schemas in VEK2 werden aktualisiert.")
    refresh_stats(
        config['OEREB2_VEK2']['connection_string'],
        config['OEREB2_VEK2']['username']
    )

    logger.info("Statistiken des ÖREB2-Schemas in VEK1 werden aktualisiert.")
    refresh_stats(
        config['OEREB2_VEK1']['connection_string'],
        config['OEREB2_VEK1']['username']
    )

    logger.info(
        "Statistiken der PostGIS-Transferstruktur in VEK2 werden aktualisiert."
    )
    refresh_stats_pg(config['OEREB_VEK2_PG']['connection_string'])

    logger.info(
        "Statistiken der PostGIS-Transferstruktur in VEK1 werden aktualisiert."
    )
    refresh_stats_pg(config['OEREB_VEK1_PG']['connection_string'])

    logger.info("Statistiken wurden aktualisiert.")