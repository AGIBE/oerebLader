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
    oereb_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], oereb_sql)
    for oereb_ebene in oereb_ebenen:
        oereb_table = oereb_ebene[0]
        oereb_liefereinheit_field = oereb_ebene[1]
        oereb_delete_sql = "DELETE FROM %s WHERE %s = %s" % (oereb_table, oereb_liefereinheit_field, liefereinheit)
        logger.info("Deleting...")
        logger.info(oereb_delete_sql)
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB_WORK']['connection_string'], oereb_delete_sql)

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
