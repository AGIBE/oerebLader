# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import logging
import os
import arcpy
import fmeobjects
import sys

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    gprcode = 'BALISKBS'
    
    table_sql = "select ebecode from gpr where GPRCODE='" + gprcode + "'"
    ebenen = config['OEREB2_WORK']['connection'].db_read(table_sql)
    ebenen_fme = []
    for ebene in ebenen:
        logger.info("Ebene " + ebene[0])
        ebene_name = gprcode + "_" + ebene[0]
        ebenen_fme.append((config['GEODB_WORK']['username'] + "." + ebene_name))
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
        
    # Eine Liste der Attribute mit Typ Date erstellen (FME braucht diese Info, damit leere Datumsfelder fuer Postgres richtig gesetzt werden koennen)
    datefields = arcpy.ListFields(source,field_type='Date')
    dfield = None
    for datefield in datefields:
        if dfield is None:
            dfield = datefield.name
        else:
            dfield = dfield + ' ' + datefield.name

    
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()

    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'GEODB_WORK': str(config['GEODB_WORK']['connection_file']),
        'GEODB_PG_DATABASE': str(config['GEODB_WORK_PG']['database']),
        'GEODB_PG_USERNAME': str(config['GEODB_WORK_PG']['username']),
        'GEODB_PG_PASSWORD': str(config['GEODB_WORK_PG']['password']),
        'GEODB_PG_HOST': str(config['GEODB_WORK_PG']['host']),
        'GEODB_PG_PORT': str(config['GEODB_WORK_PG']['port']),
        'SCHEMA_NAME': str(config['GEODB_WORK']['username']),
        'TABELLEN': str(" ".join(ebenen_fme)),
        'DATEFIELDS': str(dfield),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    # Berechtigungen in PostGIS neu setzen, da Tabellen
    # immer gelöscht und neu angelegt werden.
    for pg_ebene in ebenen_fme:
        grant_sql = "GRANT SELECT ON TABLE " + pg_ebene + " TO geodb_viewer"
        logger.info("Setze PostGIS-Berechtigung für " + pg_ebene)
        config['GEODB_WORK_PG']['connection'].db_write(grant_sql) 

            
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")