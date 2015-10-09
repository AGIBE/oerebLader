# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import sys

def run(config, ticketnr):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    config['LIEFEREINHEIT'] = {}

    # Ticket-Infos holen
    config['ticketnr'] = ticketnr
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
    