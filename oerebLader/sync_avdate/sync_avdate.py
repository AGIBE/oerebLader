# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.log_helper
import oerebLader.helpers.sql_helper
import logging
import os
import datetime
import sys

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "sync_avdate")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "sync_avdate.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "sync_avdate" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def run_sync_avdate():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    
    logger.info("Hole AV-Datum aus dem GeoDB-DD.")
    dd_sql = "select GZS_ZEITSTAND from VW_GEOPRODUKT_ZEITSTAND where GPR_BEZEICHNUNG='MOPUBE' and GZS_AKTUELL=1"
    logger.info(dd_sql)
    result = oerebLader.helpers.sql_helper.readSQL(config['GEODB_DD_TEAM']['connection_string'], dd_sql)
    if len(result) == 0:
        logger.error("Für das Geoprodukt MOPUBE konnte im DD kein aktueller Zeitstand gefunden werden.")
        logger.error("Es wird kein AV-Datum synchronisiert.")
        sys.exit()
    else:
        # Datum muss umformatiert werden. Die Verschnittfunktion
        # erwartet YYYY,MM,DD bei OEVParcelAvEffectiveDate
        avdate_formatted = result[0][0].strftime("%Y,%m,%d")
        logger.info(avdate_formatted)
        sql_avdate = "update APPCONFIGURATION set ACO_VALUE='" + avdate_formatted + "' where ACO_KEY='OEVParcelAvEffectiveDate'"
        logger.info(sql_avdate)

        # bei BaseData muss anders formatiert und im vorgegebenen
        # Text (aus Config) ersetzt werden.
        basedate_formatted = result[0][0].strftime("%d.%m.%Y")
        basedata_text_de = config['GENERAL']['basedata_template_de'].replace("$$$", basedate_formatted)
        basedata_text_fr = config['GENERAL']['basedata_template_fr'].replace("$$$", basedate_formatted)
        logger.info(basedate_formatted)
        sql_basedata_de = "update APPCONFIGURATION set ACO_VALUE='" + basedata_text_de + "' where ACO_KEY='OEVGlobalBaseDataDe'"
        sql_basedata_fr = "update APPCONFIGURATION set ACO_VALUE='" + basedata_text_fr + "' where ACO_KEY='OEVGlobalBaseDataFr'"
        logger.info(sql_basedata_de)
        logger.info(sql_basedata_fr)

        try:
            logger.info("Aktualisiere Verschnittfunktion public.")
            oerebLader.helpers.sql_helper.writeSQL(config['OEREBAPP']['connection_string'], sql_avdate)
            logger.info("Aktualisiere Verschnittfunktion CUG.")
            oerebLader.helpers.sql_helper.writeSQL(config['OEREBCUGAPP']['connection_string'], sql_avdate)
            logger.info("Aktualisiere Verschnittfunktion public 2.")
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB2APP']['connection_string'], sql_avdate)
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB2APP']['connection_string'], sql_basedata_de)
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB2APP']['connection_string'], sql_basedata_fr)
        except Exception as ex:
            logger.error("Fehler beim Updaten des AV-Datums!")
            logger.error(unicode(ex))
            logger.error("Script wird abgebrochen!")
            sys.exit()
            
        
    
    