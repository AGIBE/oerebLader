# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import sys
import tempfile
import arcpy
import datetime

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
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def create_connection_files(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    temp_directory = tempfile.mkdtemp()
    sde_filename = key + ".sde"
    connection_file = os.path.join(temp_directory, sde_filename)
    logging.info("Erzeuge Connectionfile " + connection_file)
    arcpy.CreateDatabaseConnection_management(temp_directory, sde_filename, "ORACLE", database, "DATABASE_AUTH", username, password ) 
    config[key]['connection_file'] = connection_file
    
def create_connection_string(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    connection_string = username + "/" + password + "@" + database
    config[key]['connection_string'] = connection_string

def run(config, ticketnr):
    config['ticketnr'] = ticketnr
    
    # Logging initialisieren
    init_logging(ticketnr, config)
    
    logging.info("Import wird initialisiert.")
    logging.info("Ticket-Nr: " + unicode(config['ticketnr']))
    logging.info("Konfiguration: " + unicode(config))
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # Connection-Strings zusammensetzen
    create_connection_string(config, 'GEODB_WORK')
    create_connection_string(config, 'OEREB_WORK')

    # Temporäre ArcGIS-Connectionfiles erstellen
    # Die Files werden am Schluss durch s12_finish
    # wieder gelöscht.
    create_connection_files(config, 'GEODB_WORK')
    create_connection_files(config, 'OEREB_WORK')    
    
    config['LIEFEREINHEIT'] = {}

    # Ticket-Infos holen
    logging.info("Ticket-Information holen und validieren.")
    ticket_name_sql = "SELECT liefereinheit, name, status FROM ticket WHERE id=" + unicode(ticketnr)
    ticket_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], ticket_name_sql)
    if len(ticket_result) == 1:
        ticket_status = ticket_result[0][2]
        if ticket_status == 1:
            config['ticketname'] = ticket_result[0][1]
            config['LIEFEREINHEIT']['id'] = ticket_result[0][0]
        else:
            logging.error("Falscher Ticket-Status (" + unicode(ticket_status) + ")")
            logging.error("Import wird abgebrochen!")
            sys.exit()
    else:
        pass
        #TODO: Abbruch des Scripts (keines oder mehrere Tickets mit dieser ID)

    logging.info("Ticket-Name: " + config['ticketname'])
    logging.info("Liefereinheit: " + unicode(config['LIEFEREINHEIT']['id']))
        
    # Liefereinheiten-Infos holen
    logging.info("Liefereinheiten-Informationen werden geholt.")
    liefereinheit_sql = "SELECT name, bfsnr, gpr_source, ts_source, md5, gprcode FROM liefereinheit WHERE id=" + unicode(config['LIEFEREINHEIT']['id'])
    liefereinheit_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], liefereinheit_sql)
    
    if len(liefereinheit_result) == 1:
        config['LIEFEREINHEIT']['name'] = liefereinheit_result[0][0]
        config['LIEFEREINHEIT']['bfsnr'] = liefereinheit_result[0][1]
        config['LIEFEREINHEIT']['gpr_source'] = liefereinheit_result[0][2]
        config['LIEFEREINHEIT']['ts_source'] = liefereinheit_result[0][3]
        config['LIEFEREINHEIT']['md5'] = liefereinheit_result[0][4]
        config['LIEFEREINHEIT']['gprcode'] = liefereinheit_result[0][5]
    else:
        logging.error("Keine Liefereinheit mit dieser ID gefunden.")
        logging.error("Import wird abgebrochen!")
        sys.exit()
    
    logging.info("Name der Liefereinheit: " + unicode(config['LIEFEREINHEIT']['name']))
    logging.info("BFS-Nummer: " + unicode(config['LIEFEREINHEIT']['bfsnr']))
    logging.info("Quelle Geoprodukt: " + unicode(config['LIEFEREINHEIT']['gpr_source']))
    logging.info("Quelle Transferstruktur: " + unicode(config['LIEFEREINHEIT']['ts_source']))
    logging.info("Prüfsumme: " + unicode(config['LIEFEREINHEIT']['md5']))
    logging.info("Geoprodukt-Code: " + unicode(config['LIEFEREINHEIT']['gprcode']))
  
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    