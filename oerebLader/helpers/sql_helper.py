# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle

def readSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
    
    return result_list

def writeSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)