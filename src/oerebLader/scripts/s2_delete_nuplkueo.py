# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    gprcodes = config['LIEFEREINHEIT']['gprcodes']
    gprcode_clause = "('" + "','".join(gprcodes) + "')" 

    npl_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE, GPRCODE FROM GPR WHERE GPRCODE IN " + gprcode_clause
    npl_ebenen = config['OEREB_WORK_PG']['connection'].db_read(npl_sql)
    for npl_ebene in npl_ebenen:
        npl_table = npl_ebene[3] + "_" + npl_ebene[0]
        npl_bfsnr_field = npl_ebene[1]
        npl_delete_sql = "DELETE FROM %s WHERE %s = %s" % (npl_table, npl_bfsnr_field, bfsnr)
        npl_delete_psql = "DELETE FROM geodb.%s WHERE %s = %s" % (npl_table, npl_bfsnr_field, bfsnr)
        logger.info("Lösche aus " + npl_table)
        logger.info("Oracle: " + npl_delete_sql)
        logger.info("PostGIS: " + npl_delete_psql)
        config['GEODB_WORK']['connection'].db_write(npl_delete_sql)
        config['GEODB_WORK_PG']['connection'].db_write(npl_delete_psql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")