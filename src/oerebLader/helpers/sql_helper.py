# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import psycopg2
import os

def readPSQL(connection_string, sql_statement):
    with psycopg2.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
        
    return result_list

def writePSQL(connection_string, sql_statement):
    with psycopg2.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql_statement)

def readSQL(connection_string, sql_statement):
    # Das Setzen von NLS_LANG garantiert, dass Texte aus der DB
    # als Unicode ausgeliefert werden. Wenn NLS_LANG vorher schon
    # einen Wert hatte, wird dieser anschliessend wieder gesetzt.
    # Dies weil er unter Umständen wichtig für arcpy ist (z.B.
    # Probleme beim Erzeugen des Spatial Indexes).
    nls_lang_old = ""
    if 'NLS_LANG' in os.environ:
        nls_lang_old = os.environ['NLS_LANG']
    os.environ["NLS_LANG"] = "German_Germany.UTF8"        

    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
    
    if nls_lang_old == "":
        os.environ.pop('NLS_LANG')
    else:
        os.environ['NLS_LANG'] = nls_lang_old 
    
    return result_list

def writeSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql_statement)