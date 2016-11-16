# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import arcpy

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    gprcode = 'BALISKBS'
    
    table_sql = "select ebecode from gpr where GPRCODE='" + gprcode + "'"
    ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], table_sql)
    for ebene in ebenen:
        logger.info("Ebene " + ebene[0])
        ebene_name = gprcode + "_" + ebene[0]
        source = os.path.join(config['LIEFEREINHEIT']['gpr_source'], ebene_name)
        logger.info("Quelle: " + source)
        target = os.path.join(config['GEODB_WORK']['connection_file'], config['GEODB_WORK']['username'] + "." + ebene_name)
        logger.info("Ziel: " + target)
        logger.info("Truncating...")
        arcpy.TruncateTable_management(target)
        logger.info("Appending...")
        # APPEND wird mit dem Parameter TEST ausgeführt. Allfällige (eigentlich nicht
        # erlaubte) Datenmodelländerungen würden so doch noch bemerkt.
        arcpy.Append_management(source, target, "TEST")
        
        # Check ob in Quelle und Ziel die gleiche Anzahl Records vorhanden sind
        count_source = int(arcpy.GetCount_management(source)[0])
        logger.info("Anzahl Objekte in Quell-Ebene: " + unicode(count_source))
        count_target = int(arcpy.GetCount_management(target)[0])
        logger.info("Anzahl Objekte in Ziel-Ebene: " + unicode(count_target))
        
        if count_source != count_target:
            logger.error("Anzahl Objekte in Quelle und Ziel unterschiedlich!")
            raise Exception
        else:
            logger.info("Anzahl Objekte in Quelle und Ziel identisch!")
        logger.info("Ebene " + ebene_name + " wurde kopiert.")
            
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")