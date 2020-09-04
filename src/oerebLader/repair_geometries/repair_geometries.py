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
    schema_sql = "select distinct schema from workflow_schema order by schema"
    schema_sql_results = config['OEREB_WORK_PG']['connection'].db_read(schema_sql)
    for s in schema_sql_results:
        schemas.append(s[0])

    return schemas

def count_invalid_geometries(schema, connection):
    # Geometries, die von PostGIS als ungültig deklariert werden
    invalid_geometries = 0
    invalid_geometries_sql = "select id from %s.geometry where st_isvalid(geom) = false" % (schema)
    invalid_geometries_result = connection.db_read(invalid_geometries_sql)
    if invalid_geometries_result is not None:
        invalid_geometries = invalid_geometries + len(invalid_geometries_result)
    
    return invalid_geometries

def count_mixed_geometries(schema, connection):
    # Geometrien, die sowohl eine Polygon- als auch eine
    # Line-Komponente haben (nested GeometryCollection; s. auch #6929)
    mixed_geometries = 0
    mixed_geometries_sql = "select id from %s.geometry where strpos(st_asewkt(geom), 'GEOMETRYCOLLECTION(GEOMETRYCOLLECTION(')>0" % (schema)
    mixed_geometries_result = connection.db_read(mixed_geometries_sql)
    if mixed_geometries_result is not None:
        mixed_geometries = mixed_geometries + len(mixed_geometries_result)

    return mixed_geometries

def count_empty_geometries(schema, connection):
    # Geometrien, die leer sind (s. auch #6929)
    empty_geometries = 0
    empty_geometries_sql = "select id from %s.geometry where strpos(st_asewkt(geom),'EMPTY')>0" % (schema)
    empty_geometries_result = connection.db_read(empty_geometries_sql)
    if empty_geometries_result is not None:
        empty_geometries = empty_geometries + len(empty_geometries_result)

    return empty_geometries


def run_repair_geometries(db):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("repair_geometries", config)
    db_key = 'OEREB_' + db.upper() + "_PG"
    target_connection = config[db_key]['connection']

    schemas = get_postgis_schemas(config)

    has_error_occurred = False
    error_messages = []

    for schema in schemas:
        # Ungültige Geometrien
        logger.info("Repariere ungültige Geometrien im Schema %s" % (schema))
        logger.info("Ermittle Anzahl ungültiger Geometrien...")
        invalid_geometries_count_before = count_invalid_geometries(schema, target_connection)
        logger.info("%s ungültige Geometrien gefunden." % (unicode(invalid_geometries_count_before)))
        if invalid_geometries_count_before > 0:
            logger.info("Es wird repariert.")
            repair_invalid_geometries_sql = "update %s.geometry set geom=st_makevalid(geom) where st_isvalid(geom) = false" % (schema)
            try:
                target_connection.db_write(repair_invalid_geometries_sql)
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

        # Leere Geometrien
        logger.info("Repariere leere Geometrien im Schema %s" % (schema))
        logger.info("Ermittle Anzahl leerer Geometrien...")
        empty_geometries_count_before = count_empty_geometries(schema, target_connection)
        logger.info("%s leere Geometrien gefunden." % (unicode(empty_geometries_count_before)))
        if empty_geometries_count_before > 0:
            logger.info("Es wird repariert.")
            repair_empty_geometries_sql = "delete from %s.geometry where strpos(st_asewkt(geom),'EMPTY')>0" % (schema)
            try:
                target_connection.db_write(repair_empty_geometries_sql)
            except psycopg2.DataError as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            except Exception as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            empty_geometries_count_after = count_empty_geometries(schema, target_connection)
            logger.info("Es verbleiben %s leere Geometrien." % (unicode(empty_geometries_count_after)))
        else:
            logger.info("Es wird nichts repariert.")

        # Gemischte Geometrien
        logger.info("Repariere gemischte Geometrien im Schema %s" % (schema))
        logger.info("Ermittle Anzahl gemischter Geometrien...")
        mixed_geometries_count_before = count_mixed_geometries(schema, target_connection)
        logger.info("%s gemischte Geometrien gefunden." % (unicode(mixed_geometries_count_before)))
        if mixed_geometries_count_before > 0:
            logger.info("Es wird repariert.")
            repair_mixed_geometries_sql = "update %s.geometry set geom=st_forcecollection(st_collectionextract(geom,3)) where strpos(st_asewkt(geom), 'GEOMETRYCOLLECTION(GEOMETRYCOLLECTION(')>0" % (schema)
            try:
                target_connection.db_write(repair_mixed_geometries_sql)
            except psycopg2.DataError as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            except Exception as e:
                has_error_occurred = True
                error_messages.append(e)
                logger.warn("Hier ist ein Fehler aufgetreten.")
            mixed_geometries_count_after = count_mixed_geometries(schema, target_connection)
            logger.info("Es verbleiben %s gemischte Geometrien." % (unicode(mixed_geometries_count_after)))
        else:
            logger.info("Es wird nichts repariert.")


    if has_error_occurred:
        logger.error("Beim Reparieren sind Fehler aufgetreten.")
        for msg in error_messages:
            logger.error(msg)
            sys.exit()