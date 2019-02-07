# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import cx_Oracle

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    liefereinheit = config['LIEFEREINHEIT']['id']
    oereb_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='OEREB'"
    oereb_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], oereb_sql)
    for oereb_ebene in oereb_ebenen:
        oereb_table = oereb_ebene[0]
        oereb_liefereinheit_field = oereb_ebene[1]
        oereb_delete_sql = "DELETE FROM %s WHERE %s = %s" % (oereb_table, oereb_liefereinheit_field, liefereinheit)
        logger.info("Deleting Transferstruktur Oracle...")
        logger.info(oereb_delete_sql)
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], oereb_delete_sql)

    # In einer Liefereinheit kann es mehrere Schemas haben (z.B. Nutzungsplanung oder GSK)
    oereb_pg_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='OEREB_PG' ORDER BY EBEORDER ASC"
    oereb_pg_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], oereb_pg_sql)
    for schema in config['LIEFEREINHEIT']['schemas']:
        for oereb_pg_ebene in oereb_pg_ebenen:
            oereb_pg_table = schema + "." + oereb_pg_ebene[0]
            oereb_pg_liefereinheit_field = oereb_pg_ebene[1]
            oereb_pg_delete_sql = "DELETE FROM %s WHERE %s = %s" % (oereb_pg_table, oereb_pg_liefereinheit_field, liefereinheit)
            logger.info("Deleting Transferstruktur PostGIS...")
            logger.info(oereb_pg_delete_sql)
            oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], oereb_pg_delete_sql)

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
