# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import sys
import oerebLader.check_bundesthemen.md5

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    
    # ArcGIS Connection-Files löschen
    config['GEODB_WORK']['connection'].delete_all_sde_connections()
    config['OEREB2_WORK']['connection'].delete_all_sde_connections()
    
    # Ticket-Status aktualisieren
    logger.info("Ticket-Status wird auf 2 gesetzt!")
    sql_update_ticket_status = "UPDATE ticket SET status=2 WHERE id=" + unicode(config['ticketnr'])
    try:
        config['OEREB_WORK_PG']['connection'].db_write(sql_update_ticket_status)
    except Exception as ex:
        logger.error("Fehler beim Updaten des Ticket-Status!")
        logger.error(unicode(ex))
        logger.error("Script wird abgebrochen!")
        sys.exit()
    
    # MD5-Wert aktualisieren - wenn vorhanden
    if config['LIEFEREINHEIT']['md5'] != None and config['LIEFEREINHEIT']['ts_source'] != None:
        md5_new = oerebLader.check_bundesthemen.md5.get_md5_from_zip(config['LIEFEREINHEIT']['ts_source'])
        logger.info("MD5-Wert wird auf " + md5_new  + " aktualisiert.")
        sql_update_md5 = "UPDATE liefereinheit SET md5='" + md5_new + "' WHERE ID=" + unicode(config['LIEFEREINHEIT']['id'])
        try:
            config['OEREB_WORK_PG']['connection'].db_write(sql_update_md5)
        except Exception as ex:
            logger.error("Fehler beim Updaten des Ticket-Status!")
            logger.error(unicode(ex))
            logger.error("Script wird abgebrochen!")
            sys.exit()
    
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")