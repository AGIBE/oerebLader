# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import cx_Oracle

def run(config):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    schema = 'OEREB'
    liefereinheit = config['liefereinheit']
    tables = [
        {'tablename': 'AMT', 'liefereinheit_field': 'AMT_LIEFEREINHEIT'},
        {'tablename': 'ARTIKEL', 'liefereinheit_field': 'ART_LIEFEREINHEIT'},
        {'tablename': 'DARSTELLUNGSDIENST', 'liefereinheit_field': 'DAR_LIEFEREINHEIT'},
        {'tablename': 'EIGENTUMSBESCHRAENKUNG', 'liefereinheit_field': 'EIB_LIEFEREINHEIT'},
        {'tablename': 'FLAECHE', 'liefereinheit_field': 'FLA_LIEFEREINHEIT'},
        {'tablename': 'GRUVER', 'liefereinheit_field': 'GRV_LIEFEREINHEIT'},
        {'tablename': 'HINDEF', 'liefereinheit_field': 'HID_LIEFEREINHEIT'},
        {'tablename': 'HINDEFVOR', 'liefereinheit_field': 'HDV_LIEFEREINHEIT'},
        {'tablename': 'HINVOR', 'liefereinheit_field': 'HIV_LIEFEREINHEIT'},
        {'tablename': 'HINWEIDOK', 'liefereinheit_field': 'HWD_LIEFEREINHEIT'},
        {'tablename': 'LINIE', 'liefereinheit_field': 'LIN_LIEFEREINHEIT'},
        {'tablename': 'PUNKT', 'liefereinheit_field': 'PUN_LIEFEREINHEIT'},
        {'tablename': 'VORSCHRIFT', 'liefereinheit_field': 'VOR_LIEFEREINHEIT'}
    ]
    
    with cx_Oracle.connect(config['OEREB_WORK']['connection_string']) as conn:
        cursor = conn.cursor()
        for table in tables:
            logging.info("Lösche aus Tabelle " + table['tablename'])
            sql = "DELETE FROM %s.%s WHERE %s=%s" % (schema, table['tablename'], table['liefereinheit_field'], liefereinheit)
            logging.info(sql)
            cursor.execute(sql)
        
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")
