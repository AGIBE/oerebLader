# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import oerebLader.helpers.sql_helper

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    #TODO: Rückbau auf nur noch ein Geoprodukt
    npl_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE, GPRCODE FROM GPR WHERE GPRCODE IN ('NPLWALD', 'NUPLWALD')"
    npl_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], npl_sql)
    for npl_ebene in npl_ebenen:
        npl_table = npl_ebene[3] + "_" + npl_ebene[0]
        npl_bfsnr_field = npl_ebene[1]
        npl_delete_sql = "DELETE FROM %s WHERE %s = %s" % (npl_table, npl_bfsnr_field, bfsnr)
        logger.info("Lösche aus " + npl_table)
        logger.info(npl_delete_sql)
        oerebLader.helpers.sql_helper.writeSQL(config['GEODB_WORK']['connection_string'], npl_delete_sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")