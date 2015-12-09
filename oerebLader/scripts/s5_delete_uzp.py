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
    #TODO: Tabellennamen aus Tabelle GPR auslesen
    tables = [
                'UZP_BAU',
                'UZP_LSG',
                'UZP_UEO',
                'UZP_USP'
             ]
    # UZP_QUALIZP wird nicht gelöscht, weil hier ein Update reicht (in s17)
    # QUALIZPT und ZONET werden nicht gelöscht, weil beides statische
    # Wertetabellen sind.
    
    with cx_Oracle.connect(config['GEODB_WORK']['connection_string']) as conn:
        cursor = conn.cursor()
        for table in tables:
            tablename = schema + "." + table
            logger.info("Lösche aus Tabelle " + tablename)
            sql = "DELETE FROM %s WHERE BFS=%s" % (tablename, bfsnr)
            logger.info(sql)
            cursor.execute(sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")