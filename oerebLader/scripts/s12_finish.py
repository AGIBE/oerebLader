# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import sys
import oerebLader.helpers.md5_helper
import oerebLader.helpers.sql_helper

def run(config):
    logging.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # ArcGIS Connection-Files löschen
    logging.info("Lösche Connectionfile " + config['GEODB_WORK']['connection_file'])
    os.remove(config['GEODB_WORK']['connection_file'])
    logging.info("Lösche Connectionfile " + config['OEREB_WORK']['connection_file'])
    os.remove(config['OEREB_WORK']['connection_file'])
    
    # Ticket-Status aktualisieren
    logging.info("Ticket-Status wird auf 2 gesetzt!")
    sql_update_ticket_status = "UPDATE ticket SET status=2 WHERE id=" + unicode(config['ticketnr'])
    try:
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB_WORK']['connection_string'], sql_update_ticket_status)
    except Exception as ex:
        logging.error("Fehler beim Updaten des Ticket-Status!")
        logging.error(unicode(ex))
        logging.error("Script wird abgebrochen!")
        sys.exit()
    
    # MD5-Wert aktualisieren - wenn vorhanden
    if config['LIEFEREINHEIT']['md5'] != None and config['LIEFEREINHEIT']['ts_source'] != None:
        md5_new =  oerebLader.helpers.md5_helper.get_md5_from_zip(config['LIEFEREINHEIT']['ts_source'])
        logging.info("MD5-Wert wird auf " + md5_new  + " aktualisiert.")
        sql_update_md5 = "UPDATE liefereinheit SET md5='" + md5_new + "' WHERE ID=" + unicode(config['LIEFEREINHEIT']['id'])
        try:
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB_WORK']['connection_string'], sql_update_md5)
        except Exception as ex:
            logging.error("Fehler beim Updaten des Ticket-Status!")
            logging.error(unicode(ex))
            logging.error("Script wird abgebrochen!")
            sys.exit()
    
    logging.info("Script " +  os.path.basename(__file__) + " ist beendet.")