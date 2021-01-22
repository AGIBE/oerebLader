# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import oerebLader.config
import oerebLader.logging
import oerebLader.check_bundesthemen.md5
import os
import logging
import datetime
import sys

def get_liefereinheit_info(liefereinheit, config):
    logger = logging.getLogger("oerebLaderLogger")
    logger.info("Liefereinheiten-Informationen werden geholt.")
    liefereinheit_sql = "SELECT name, bfsnr, gpr_source, ts_source, md5 FROM liefereinheit where id=" + unicode(liefereinheit)
    liefereinheit_result = config['OEREB_WORK_PG']['connection'].db_read(liefereinheit_sql)
    
    liefereinheit_info = {}

    if len(liefereinheit_result) == 1:
        liefereinheit_info['name'] = liefereinheit_result[0][0]
        liefereinheit_info['bfsnr'] = liefereinheit_result[0][1]
        liefereinheit_info['gpr_source'] = liefereinheit_result[0][2]
        liefereinheit_info['ts_source'] = liefereinheit_result[0][3]
        liefereinheit_info['md5_old'] = liefereinheit_result[0][4]
    else:
        logger.error("Keine Liefereinheit mit dieser ID gefunden.")
        logger.error("Import wird abgebrochen!")
        sys.exit()
    
    return liefereinheit_info

def create_ticket(liefereinheit, config):
    logger = logging.getLogger("oerebLaderLogger")
    name = "Aktualisierung vom " + datetime.datetime.now().strftime("%d.%m.%Y")
    create_ticket_sql = "INSERT INTO ticket (liefereinheit, status, art, name, nachfuehrung) VALUES (%s, %s, %s, '%s', CURRENT_DATE)" % (liefereinheit, 1, 5, name)
    logger.info(create_ticket_sql)
    try:
        config['OEREB_WORK_PG']['connection'].db_write(create_ticket_sql)
    except Exception as ex:
        logger.error("Fehler beim Einfügen des Tickets!")
        logger.error(unicode(ex))
        logger.error("Script wird abgebrochen!")
        sys.exit()
    logger.info("Ticket wurde erstellt!")
    logger.info("Hole Ticket-Nummer.")
    ticket_sql = "SELECT id FROM ticket WHERE name='%s' and liefereinheit=%s and status=1 and art=5" % (name, liefereinheit)
    ticket_results = config['OEREB_WORK_PG']['connection'].db_read(ticket_sql)
    ticketnr = unicode(ticket_results[0][0])
    logger.info("Ticket-Nummer lautet: %s" % (ticketnr))
    return ticketnr

def run_check_bundesthemen():
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("check_bundesthemen", config)
    
    liefereinheiten = config['GENERAL']['bundesthemen']
    config['LIEFEREINHEIT'] = {}
    
    for liefereinheit in liefereinheiten:
        liefereinheit_info = get_liefereinheit_info(liefereinheit, config)
        logger.info("ID der Liefereinheit: " + unicode(liefereinheit))
        logger.info("Name der Liefereinheit: " + unicode(liefereinheit_info['name']))
        logger.info("Quelle Transferstruktur: " + unicode(liefereinheit_info['ts_source']))
        logger.info("Prüfsumme: " + unicode(liefereinheit_info['md5_old']))
        
        logging.info("MD5-Wert wird heruntergeladen!")
        liefereinheit_info['md5_new'] = oerebLader.check_bundesthemen.md5.get_md5_from_zip(liefereinheit_info['ts_source'])
        logger.info("Neuer MD5-Wert: " + liefereinheit_info['md5_new'])
        logger.info("Vergleiche MD5: " + liefereinheit_info['md5_old'] + " vs. " + liefereinheit_info['md5_new'])
        
        if liefereinheit_info['md5_old'] != liefereinheit_info['md5_new']:
            ticketnr = create_ticket(liefereinheit, config)
            logger.info("Für die Liefereinheit %s (%s) wurde das Ticket %s angelegt." % (unicode(liefereinheit), liefereinheit_info['name'], unicode(ticketnr)))
            
        else:
            logger.info("Prüfsummen sind identisch. Keine Aktualisierung notwendig!")
        
    print("CheckBundesthemen SUCCESSFUL!")