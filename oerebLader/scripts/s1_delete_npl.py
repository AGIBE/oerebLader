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
                'NPL_ABGRENZ',
                'NPL_GEFF',
                'NPL_GNBAUW',
                'NPL_GNGU',
                'NPL_GNGZ',
                'NPL_GNNUTZZO',
                'NPL_NHSF',
                'NPL_NHSL',
                'NPL_NHSP',
                'NPL_RVT',
                'NPL_RVT_VORSORT',
                'NPL_UELAERM',
                'NPL_UEPROJ',
                'NPL_UEUL',
                'NPL_UEUZ',
                'NPL_UEWAAB',
                'NPL_VEFE',
                'NPL_WAABPER',
                'NPL_WEWRF',
                'NPL_WEWRL',
                'NPL_GEGEWF',
                'NPL_GEGEWL' 
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
