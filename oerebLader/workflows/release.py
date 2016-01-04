# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.log_helper
import oerebLader.helpers.connection_helper
import oerebLader.helpers.sql_helper
import os
import datetime
import logging
import arcpy

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "release") 
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "release_" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log")
    
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_release():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Der Release wird initialisiert!")
    
    # Connection-Files erstellen
    config['GEODB_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'GEODB_WORK', logger)
    config['OEREB_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'OEREB_WORK', logger)    
    config['NORM_TEAM']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'NORM_TEAM', logger)
    config['OEREB_TEAM']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'OEREB_TEAM', logger)    
    
    logger.info("Folgende Tickets werden released:")
    ticket_sql = "select ticket.ID, liefereinheit.ID, liefereinheit.NAME, liefereinheit.BFSNR, liefereinheit.GPRCODE from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.id where ticket.STATUS=3"
    tickets = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], ticket_sql)
    liefereinheiten = []
    #Geoprodukt kopieren
    logger.info("Das Geoprodukt wird freigegeben.")
    for ticket in tickets:
        logger.info("ID: " + unicode(ticket[0]) + "/ Liefereinheit: " + unicode(ticket[1]) + " / GPRCODE: " + ticket[4])
        liefereinheiten.append(unicode(ticket[1]))
        #TODO: im Fall NPL noch UZP und OEREBSTA einbauen
        gpr_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='" + ticket[4] + "'"
        ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], gpr_sql)
        for ebene in ebenen:
            ebene_name = ticket[4] + "_" + ebene[0]
            source = os.path.join(config['GEODB_WORK']['connection_file'], config['GEODB_WORK']['username'] + "." + ebene_name)
            source_layer = ebene_name + "_" + unicode(ticket[3])
            target = os.path.join(config['NORM_TEAM']['connection_file'], config['NORM_TEAM']['username'] + "." + ebene_name)
            target_layer = "target_" + ebene_name + "_" + unicode(ticket[3])
            where_clause = ""
            delete_sql = "DELETE FROM " + ebene_name
            if ebene[1] is not None:
                if ebene[2] == 'BFSNR':
                    where_clause = ebene[1] + "=" + unicode(ticket[3])
                elif ebene[2] == 'LIEFEREINHEIT':
                    where_clause = ebene[1] + "=" + unicode(ticket[1])
                delete_sql = delete_sql + " WHERE " + where_clause
            if arcpy.Describe(source).datasetType=='Table':
                if where_clause == "":
                    arcpy.MakeTableView_management(source, source_layer)
                    arcpy.MakeTableView_management(target, target_layer)
                else:
                    arcpy.MakeTableView_management(source, source_layer, where_clause)
                    arcpy.MakeTableView_management(target, target_layer, where_clause)
            else:
                if where_clause == "":
                    arcpy.MakeFeatureLayer_management(source, source_layer)
                    arcpy.MakeFeatureLayer_management(target, target_layer)
                else:
                    arcpy.MakeFeatureLayer_management(source, source_layer, where_clause)
                    arcpy.MakeFeatureLayer_management(target, target_layer, where_clause)

            logger.info("Deleting...")
            logger.info(delete_sql)
            oerebLader.helpers.sql_helper.writeSQL(config['NORM_TEAM']['connection_string'], delete_sql)
            logger.info("Appending...")
            arcpy.Append_management(source_layer, target, "TEST")
            logger.info("Counting..")
            source_count = int(arcpy.GetCount_management(source_layer)[0])
            logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
            target_count = int(arcpy.GetCount_management(target_layer)[0])
            logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
            if source_count!=target_count:
                logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
    
    # Transferstruktur kopieren
    liefereinheiten_joined = "(" + ",".join(liefereinheiten) + ")"
    oereb_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='OEREB'"
    oereb_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], oereb_sql)
    for oereb_ebene in oereb_ebenen:
        oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_ebene[0], oereb_ebene[1], liefereinheiten_joined)
        logger.info("Deleteing...")
        logger.info(oereb_delete_sql)
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB_TEAM']['connection_string'], oereb_delete_sql)
    logger.info("Löschen abgeschlossen.")
    logger.info("Daten werden kopiert.") 

                
    #TODO: Transferstruktur (enthält reine Oracle-Tabellen)
    #TODO: Ticket-Status erhöhen
    #TODO: GeoDB-Tabellen schreiben (Flag, Task)
    
    # Connection-Files löschen
    oerebLader.helpers.connection_helper.delete_connection_files(config['GEODB_WORK']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['OEREB_WORK']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['NORM_TEAM']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['OEREB_TEAM']['connection_file'], logger)