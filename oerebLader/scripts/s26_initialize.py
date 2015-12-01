# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import oerebLader.helpers.log_helper
import oerebLader.helpers.connection_helper
import logging
import os
import sys
import tempfile
import arcpy
import datetime
import chromalog

def init_logging(ticketnr, config):
    log_directory = os.path.join(config['LOGGING']['basedir'], unicode(ticketnr))
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, unicode(ticketnr) + ".log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = unicode(ticketnr) + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run(config, ticketnr):
    config['ticketnr'] = ticketnr
    
    # Logging initialisieren
    logger = init_logging(ticketnr, config)
    
    logger.info("Import wird initialisiert.")
    logger.info("Ticket-Nr: " + unicode(config['ticketnr']))
    logger.info("Konfiguration: " + unicode(config))
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # Temporäre ArcGIS-Connectionfiles erstellen
    # Die Files werden am Schluss durch s12_finish
    # wieder gelöscht.
    config['GEODB_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'GEODB_WORK', logger)
    config['OEREB_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'OEREB_WORK', logger)    
    
    config['LIEFEREINHEIT'] = {}

    # Ticket-Infos holen
    logger.info("Ticket-Information holen und validieren.")
    ticket_name_sql = "SELECT liefereinheit, name, status FROM ticket WHERE id=" + unicode(ticketnr)
    ticket_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], ticket_name_sql)
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
        pass
        #TODO: Abbruch des Scripts (keines oder mehrere Tickets mit dieser ID)

    logger.info("Ticket-Name: " + config['ticketname'])
    logger.info("Liefereinheit: " + unicode(config['LIEFEREINHEIT']['id']))
        
    # Liefereinheiten-Infos holen
    logger.info("Liefereinheiten-Informationen werden geholt.")
    liefereinheit_sql = "SELECT name, bfsnr, gpr_source, ts_source, md5, gprcode FROM liefereinheit WHERE id=" + unicode(config['LIEFEREINHEIT']['id'])
    liefereinheit_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], liefereinheit_sql)
    
    if len(liefereinheit_result) == 1:
        config['LIEFEREINHEIT']['name'] = liefereinheit_result[0][0]
        config['LIEFEREINHEIT']['bfsnr'] = liefereinheit_result[0][1]
        if config['LIEFEREINHEIT']['bfsnr'] > 0:
            gemeinde_name_sql = "SELECT bfs_name FROM bfs WHERE bfs_nr=" + unicode(config['LIEFEREINHEIT']['bfsnr'])
            gemeinde_name_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'],gemeinde_name_sql)
            config['LIEFEREINHEIT']['gemeinde_name'] = gemeinde_name_result[0][0]
        else:
            config['LIEFEREINHEIT']['gemeinde_name'] = None
        config['LIEFEREINHEIT']['gpr_source'] = liefereinheit_result[0][2]
        config['LIEFEREINHEIT']['ts_source'] = liefereinheit_result[0][3]
        config['LIEFEREINHEIT']['md5'] = liefereinheit_result[0][4]
        config['LIEFEREINHEIT']['gprcode'] = liefereinheit_result[0][5]
    else:
        logger.error("Keine Liefereinheit mit dieser ID gefunden.")
        logger.error("Import wird abgebrochen!")
        sys.exit()
    
    logger.info("Name der Liefereinheit: " + unicode(config['LIEFEREINHEIT']['name']))
    logger.info("BFS-Nummer: " + unicode(config['LIEFEREINHEIT']['bfsnr']))
    logger.info("Gemeindename: " + unicode(config['LIEFEREINHEIT']['gemeinde_name']))
    logger.info("Quelle Geoprodukt: " + unicode(config['LIEFEREINHEIT']['gpr_source']))
    logger.info("Quelle Transferstruktur: " + unicode(config['LIEFEREINHEIT']['ts_source']))
    logger.info("Prüfsumme: " + unicode(config['LIEFEREINHEIT']['md5']))
    logger.info("Geoprodukt-Code: " + unicode(config['LIEFEREINHEIT']['gprcode']))
  
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    