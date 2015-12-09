# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import cx_Oracle

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    schema = 'GEODB'
    tables = [
                'NPLKUEO_UEKUEO',
                'NPLKUEO_KUEORVT'
             ]
    
    with cx_Oracle.connect(config['GEODB_WORK']['connection_string']) as conn:
        cursor = conn.cursor()
        for table in tables:
            tablename = schema + "." + table
            logger.info("Lösche aus Tabelle " + tablename)
            sql = "DELETE FROM %s WHERE BFSNR=%s" % (tablename, bfsnr)
            logger.info(sql)
            cursor.execute(sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
