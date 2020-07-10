# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.logging
import oerebLader.helpers.sql_helper
import logging
import os
import datetime
import sys

def run_sync_avdate():
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("sync_avdate", config)
    
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
            
        
    
    