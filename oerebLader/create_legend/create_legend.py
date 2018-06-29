# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import oerebLader.helpers.legend_helper

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "create_legend")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "create_legend.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "build_map" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def get_all_liefereinheiten(config):
    liefereinheiten_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit like '___01' order by eib_liefereinheit"
    liefereinheiten_list = []
    
    liefereinheiten_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], liefereinheiten_sql)
    
    for row in liefereinheiten_result:
        liefereinheiten_list.append(row[0])
        
    return liefereinheiten_list

def get_single_liefereinheit(bfsnr, config):
    
    liefereinheit = unicode(bfsnr) + "01"
        
    liefereinheit_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + liefereinheit
    
    liefereinheit_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], liefereinheit_sql)
    
    if len(liefereinheit_result)==1:
        return liefereinheit
    else:
        return None
        

def run_create_legend(bfsnr):
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    
    liefereinheiten = []
    
    if bfsnr==9999:
        logger.info("Es werden die Legenden sämtlicher aufgeschalteten Gemeinden erstellt.")
        liefereinheiten = get_all_liefereinheiten(config)
    else:
        logger.info("Es wird die Legende der Gemeinde " + unicode(bfsnr) + " erstellt.")
        liefereinheit = get_single_liefereinheit(bfsnr, config)
        if liefereinheit is not None:
            liefereinheiten.append(liefereinheit)
    
    logger.info("Es werden die Legenden folgender Gemeinden erstellt:")
    for le in liefereinheiten:
        logger.info(le)
    
    logger.info("Legenden werden erstellt.")

