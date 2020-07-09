# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import oerebLader.helpers.config
import oerebLader.helpers.md5_helper
import oerebLader.helpers.sql_helper
import os
import logging
import datetime
import sys

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], 'bundesthemen')
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile_name = "bundesthemen" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
    logfile = os.path.join(log_directory, logfile_name)
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    print("Logfile: " + logfile)

def get_liefereinheit_info(liefereinheit, config):
    logging.info("Liefereinheiten-Informationen werden geholt.")
    liefereinheit_sql = "SELECT name, bfsnr, gpr_source, ts_source, md5 FROM liefereinheit where id=" + unicode(liefereinheit)
    liefereinheit_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], liefereinheit_sql)
    
    liefereinheit_info = {}

    if len(liefereinheit_result) == 1:
        liefereinheit_info['name'] = liefereinheit_result[0][0]
        liefereinheit_info['bfsnr'] = liefereinheit_result[0][1]
        liefereinheit_info['gpr_source'] = liefereinheit_result[0][2]
        liefereinheit_info['ts_source'] = liefereinheit_result[0][3]
        liefereinheit_info['md5_old'] = liefereinheit_result[0][4]
    else:
        logging.error("Keine Liefereinheit mit dieser ID gefunden.")
        logging.error("Import wird abgebrochen!")
        sys.exit()
    
    return liefereinheit_info

def create_ticket(liefereinheit, config):
    name = "Aktualisierung vom " + datetime.datetime.now().strftime("%d.%m.%Y")
    create_ticket_sql = "INSERT INTO ticket (liefereinheit, status, art, name, nachfuehrung) VALUES (%s, %s, %s, '%s', SYSDATE)" % (liefereinheit, 1, 5, name)
    logging.info(create_ticket_sql)
    try:
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], create_ticket_sql)
    except Exception as ex:
        logging.error("Fehler beim Einfügen des Tickets!")
        logging.error(unicode(ex))
        logging.error("Script wird abgebrochen!")
        sys.exit()
    logging.info("Ticket wurde erstellt!")

def check_bundesthemen():
    config = oerebLader.helpers.config.get_config()
    
    liefereinheiten = config['GENERAL']['bundesthemen']
    config['LIEFEREINHEIT'] = {}
    
    init_logging(config)
    
    for liefereinheit in liefereinheiten:
        liefereinheit_info = get_liefereinheit_info(liefereinheit, config)
        logging.info("ID der Liefereinheit: " + unicode(liefereinheit))
        logging.info("Name der Liefereinheit: " + unicode(liefereinheit_info['name']))
        logging.info("Quelle Transferstruktur: " + unicode(liefereinheit_info['ts_source']))
        logging.info("Prüfsumme: " + unicode(liefereinheit_info['md5_old']))
        
        logging.info("MD5-Wert wird heruntergeladen!")
        liefereinheit_info['md5_new'] = oerebLader.helpers.md5_helper.get_md5_from_zip(liefereinheit_info['ts_source'])
        logging.info("Neuer MD5-Wert: " + liefereinheit_info['md5_new'])
        logging.info("Vergleiche MD5: " + liefereinheit_info['md5_old'] + " vs. " + liefereinheit_info['md5_new'])
        
        if liefereinheit_info['md5_old'] != liefereinheit_info['md5_new']:
            logging.info("Für die Liefereinheit " + unicode(liefereinheit) + " (" + liefereinheit_info['name'] + ") wird ein neues Ticket angelegt.")
            create_ticket(liefereinheit, config)
        else:
            logging.info("Prüfsummen sind identisch. Keine Aktualisierung notwendig!")
        
    print("CheckBundesthemen SUCCESSFUL!")