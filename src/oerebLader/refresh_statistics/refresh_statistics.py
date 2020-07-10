# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.logging
import os
import datetime
import cx_Oracle
import psycopg2


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
    logger = oerebLader.logging.init_logging("refresh_statistics", config)

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