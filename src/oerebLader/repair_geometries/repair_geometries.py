# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.config
import oerebLader.logging
import logging
import datetime
import psycopg2
import os
import sys

def get_postgis_schemas(config):
    schemas = []
    schema_sql = "select distinct schema from oereb2.workflow_schema order by schema"
    schema_sql_results = config['OEREB_WORK_PG']['connection'].db_read(schema_sql)
    for s in schema_sql_results:
        schemas.append(s[0])

    return schemas

def count_invalid_geometries(schema, connection):
    invalid_geometries_sql = "select id from %s.geometry where st_isvalid(geom) = false" % (schema)
    invalid_geometries_result = connection.db_read(invalid_geometries_sql)
    if invalid_geometries_result is None:
        return 0
    else:
        return len(invalid_geometries_result)

def run_repair_geometries(db):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("repair_geometries", config)
    db_key = 'OEREB_' + db.upper() + "_PG"
    target_connection = config[db_key]['connection']

    schemas = get_postgis_schemas(config)

    has_error_occurred = False
    error_messages = []

    for schema in schemas:
        logger.info("Repariere im Schema %s" % (schema))
        logger.info("Ermittle Anzahl ungültiger Geometrien...")
        invalid_geometries_count_before = count_invalid_geometries(schema, target_connection)
        logger.info("%s ungültige Geometrien gefunden." % (unicode(invalid_geometries_count_before)))
        if invalid_geometries_count_before > 0:
            logger.info("Es wird repariert.")
            repair_geometries_sql = "update %s.geometry set geom=st_makevalid(geom) where st_isvalid(geom) = false" % (schema)
            try:
                target_connection.db_write(repair_geometries_sql)
            except psycopg2.DataError as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            except Exception as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            invalid_geometries_count_after = count_invalid_geometries(schema, target_connection)
            logger.info("Es verbleiben %s ungültige Geometrien." % (unicode(invalid_geometries_count_after)))
        else:
            logger.info("Es wird nichts repariert.")

    if has_error_occurred:
        logger.error("Beim Reparieren sind Fehler aufgetreten.")
        for msg in error_messages:
            logger.error(msg)
            sys.exit()