# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.connection
import oerebLader.logging
import oerebLader.helpers.excel_helper
import logging
import os
import sys
import arcpy
import datetime

def run(config, ticketnr):
    config['ticketnr'] = ticketnr
    
    # Logging initialisieren
    logger = oerebLader.logging.init_logging(unicode(ticketnr), config)
    
    logger.info("Import wird initialisiert.")
    logger.info("Ticket-Nr: " + unicode(config['ticketnr']))
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")

    # Temporäre ArcGIS-Connectionfiles erstellen
    # Die Files werden am Schluss durch s12_finish
    # wieder gelöscht.
    config['GEODB_WORK']['connection_file'] = config['GEODB_WORK']['connection'].create_sde_connection()
    config['GEODB_WORK']['connection_file'] = config['OEREB2_WORK']['connection'].create_sde_connection()
    
    config['LIEFEREINHEIT'] = {}

    # Ticket-Infos holen
    logger.info("Ticket-Information holen und validieren.")
    ticket_name_sql = "SELECT liefereinheit, name, status FROM ticket WHERE id=" + unicode(ticketnr)
    ticket_result = config['OEREB_WORK_PG']['connection'].db_read(ticket_name_sql)
    if len(ticket_result) == 1:
        ticket_status = ticket_result[0][2]
        if ticket_status == 1:
            config['ticketname'] = ticket_result[0][1]
            config['LIEFEREINHEIT']['id'] = ticket_result[0][0]
        else:
            logger.error("Falscher Ticket-Status (" + unicode(ticket_status) + ")")
            logger.error("Import wird abgebrochen!")
            sys.exit()
    else:
        logger.error("Es gibt kein Ticket mit dieser ID.")
        logger.error("Import kann nicht ausgeführt werden.")
        sys.exit()

    logger.info("Ticket-Name: " + config['ticketname'])
    logger.info("Liefereinheit: " + unicode(config['LIEFEREINHEIT']['id']))
        
    # Liefereinheiten-Infos holen
    logger.info("Liefereinheiten-Informationen werden geholt.")
    liefereinheit_sql = "SELECT name, bfsnr, gpr_source, ts_source, md5, workflow FROM liefereinheit WHERE id=" + unicode(config['LIEFEREINHEIT']['id'])
    liefereinheit_result = config['OEREB_WORK_PG']['connection'].db_read(liefereinheit_sql)
    
    if len(liefereinheit_result) == 1:
        config['LIEFEREINHEIT']['name'] = liefereinheit_result[0][0]
        config['LIEFEREINHEIT']['bfsnr'] = liefereinheit_result[0][1]
        if config['LIEFEREINHEIT']['bfsnr'] > 0:
            gemeinde_name_sql = "SELECT bfs_name FROM bfs WHERE bfs_nr=" + unicode(config['LIEFEREINHEIT']['bfsnr'])
            gemeinde_name_result = config['OEREB_WORK_PG']['connection'].db_read(gemeinde_name_sql)
            config['LIEFEREINHEIT']['gemeinde_name'] = gemeinde_name_result[0][0]
        else:
            config['LIEFEREINHEIT']['gemeinde_name'] = None
        config['LIEFEREINHEIT']['gpr_source'] = liefereinheit_result[0][2]
        config['LIEFEREINHEIT']['ts_source'] = liefereinheit_result[0][3]
        config['LIEFEREINHEIT']['md5'] = liefereinheit_result[0][4]
        config['LIEFEREINHEIT']['workflow'] = liefereinheit_result[0][5]
    else:
        logger.error("Keine Liefereinheit mit dieser ID gefunden.")
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    # GPRCODES holen
    logger.info("GPR-Infos werden geholt.")
    gpr_sql = "SELECT gprcode FROM workflow_gpr WHERE workflow='" + config['LIEFEREINHEIT']['workflow'] + "'"
    gpr_result = config['OEREB_WORK_PG']['connection'].db_read(gpr_sql)
    gpr_codes = []
    if len(gpr_result) > 0:
        for gpr in gpr_result:
            gpr_codes.append(gpr[0])
        config['LIEFEREINHEIT']['gprcodes'] = gpr_codes
    else:
        logger.error("Für den Workflow konnte keine Geoprodukt-Definiton gefunden werden.")
        logger.error("Import wird abgebrochen.")
        sys.exit()
    
    # POSTGIS-SCHEMAS holen
    logger.info("PostGIS-Schemas werden geholt.")
    schema_sql = "SELECT schema FROM workflow_schema WHERE workflow='" + config['LIEFEREINHEIT']['workflow'] + "'"
    schema_result = config['OEREB_WORK_PG']['connection'].db_read(schema_sql)
    schemas = []
    if len(schema_result) > 0:
        for schema in schema_result:
            schemas.append(schema[0])
        config['LIEFEREINHEIT']['schemas'] = schemas
    else:
        logger.error("Für den Workflow konnten keine PostGIS-Schemas gefunden werden.")
        logger.error("Import wird abgebrochen.")
        sys.exit()

    # AMT_OID aus zentraler AMT-Tabelle holen (für Bundesthemen == -99)
    logger.info("AMT_OID wird aus zentraler AMT-Tabelle geholt.")
    ar = oerebLader.helpers.excel_helper.AmtReader(config['GENERAL']['amt_tabelle'], "AMT")
    amt_oids = ar.get_oid_by_liefereinheit(config['LIEFEREINHEIT']['id'])
    config['LIEFEREINHEIT']['amt_oid'] = amt_oids[0]
    config['LIEFEREINHEIT']['amt_oid_base'] = amt_oids[1]

    logger.info("Name der Liefereinheit: " + unicode(config['LIEFEREINHEIT']['name']))
    logger.info("BFS-Nummer: " + unicode(config['LIEFEREINHEIT']['bfsnr']))
    logger.info("Gemeindename: " + unicode(config['LIEFEREINHEIT']['gemeinde_name']))
    logger.info("Quelle Geoprodukt: " + unicode(config['LIEFEREINHEIT']['gpr_source']))
    logger.info("Quelle Transferstruktur: " + unicode(config['LIEFEREINHEIT']['ts_source']))
    logger.info("Prüfsumme: " + unicode(config['LIEFEREINHEIT']['md5']))
    logger.info("Workflow: " + unicode(config['LIEFEREINHEIT']['workflow']))
    logger.info("Geoprodukt-Code(s): " + unicode(",".join(config['LIEFEREINHEIT']['gprcodes'])))
    logger.info("PostGIS-Schema(s): " + unicode(",".join(config['LIEFEREINHEIT']['schemas'])))
    logger.info("AMT_OID: " + unicode(config['LIEFEREINHEIT']['amt_oid']))
    logger.info("AMT_OID_BASE: " + unicode(config['LIEFEREINHEIT']['amt_oid_base']))
  
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    