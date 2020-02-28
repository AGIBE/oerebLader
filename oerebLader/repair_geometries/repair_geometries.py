# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.log_helper
import oerebLader.helpers.sql_helper
import psycopg2
import logging
import datetime
import os
import sys

def get_postgis_schemas(config):
    schemas = []
    schema_sql = "select distinct schema from oereb2.workflow_schema order by schema"
    schema_sql_results = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], schema_sql)
    for s in schema_sql_results:
        schemas.append(s[0])

    return schemas

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "repair_geometries")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "repair_geometries.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "repair_geometries" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def count_invalid_geometries(schema, connection_string):
    invalid_geometries_sql = "select id from %s.geometry where st_isvalid(geom) = false" % (schema)
    invalid_geometries_result = oerebLader.helpers.sql_helper.readPSQL(connection_string, invalid_geometries_sql)
    if invalid_geometries_result is None:
        return 0
    else:
        return len(invalid_geometries_result)


def run_repair_geometries(db):
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    db_key = 'OEREB_' + db.upper() + "_PG"
    target_connection_string = config[db_key]['connection_string']

    schemas = get_postgis_schemas(config)

    has_error_occurred = False
    error_messages = []

    for schema in schemas:
        logger.info("Repariere im Schema %s" % (schema))
        logger.info("Ermittle Anzahl ungültiger Geometrien...")
        invalid_geometries_count_before = count_invalid_geometries(schema, target_connection_string)
        logger.info("%s ungültige Geometrien gefunden." % (unicode(invalid_geometries_count_before)))
        if invalid_geometries_count_before > 0:
            logger.info("Es wird repariert.")
            repair_geometries_sql = "update %s.geometry set geom=st_makevalid(geom) where st_isvalid(geom) = false" % (schema)
            try:
                oerebLader.helpers.sql_helper.writePSQL(target_connection_string, repair_geometries_sql)
            except psycopg2.DataError as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            except Exception as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            invalid_geometries_count_after = count_invalid_geometries(schema, target_connection_string)
            logger.info("Es verbleiben %s ungültige Geometrien." % (unicode(invalid_geometries_count_after)))
        else:
            logger.info("Es wird nichts repariert.")

    if has_error_occurred:
        logger.error("Beim Reparieren sind Fehler aufgetreten.")
        for msg in error_messages:
            logger.error(msg)
            sys.exit()