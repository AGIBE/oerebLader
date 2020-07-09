# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import sys
import oerebLader.helpers.md5_helper
import oerebLader.helpers.sql_helper
import oerebLader.helpers.connection_helper

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # ArcGIS Connection-Files löschen
    oerebLader.helpers.connection_helper.delete_connection_files(config['GEODB_WORK']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['OEREB2_WORK']['connection_file'], logger)
    
    # Ticket-Status aktualisieren
    logger.info("Ticket-Status wird auf 2 gesetzt!")
    sql_update_ticket_status = "UPDATE ticket SET status=2 WHERE id=" + unicode(config['ticketnr'])
    try:
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], sql_update_ticket_status)
    except Exception as ex:
        logger.error("Fehler beim Updaten des Ticket-Status!")
        logger.error(unicode(ex))
        logger.error("Script wird abgebrochen!")
        sys.exit()
    
    # MD5-Wert aktualisieren - wenn vorhanden
    if config['LIEFEREINHEIT']['md5'] != None and config['LIEFEREINHEIT']['ts_source'] != None:
        md5_new =  oerebLader.helpers.md5_helper.get_md5_from_zip(config['LIEFEREINHEIT']['ts_source'])
        logger.info("MD5-Wert wird auf " + md5_new  + " aktualisiert.")
        sql_update_md5 = "UPDATE liefereinheit SET md5='" + md5_new + "' WHERE ID=" + unicode(config['LIEFEREINHEIT']['id'])
        try:
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], sql_update_md5)
        except Exception as ex:
            logger.error("Fehler beim Updaten des Ticket-Status!")
            logger.error(unicode(ex))
            logger.error("Script wird abgebrochen!")
            sys.exit()
    
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")