# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import sys
import urlparse
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

def get_liefereinheiten(config, bfsnr=9999):
    
    liefereinheiten_list = []
    
    # Wenn bfsnr=9999 werden alle Liefereinheiten abgefragt.
    # Wenn bfsnr einen Wert hat, wird nur diese Liefereinheit abgefragt.
    if bfsnr == 9999:
        liefereinheiten_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit like '___01' order by eib_liefereinheit"
    else:
        liefereinheit = unicode(bfsnr) + "01"
        liefereinheiten_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + liefereinheit
        
    liefereinheiten_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], liefereinheiten_sql)
    
    for row in liefereinheiten_result:
        liefereinheiten_list.append(unicode(row[0]))
        
    return liefereinheiten_list

def get_bfsnr(config, liefereinheit):
    bfsnr_sql = "select bfsnr from liefereinheit where id=" + unicode(liefereinheit)
    
    bfsnr_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], bfsnr_sql)
    print(liefereinheit)
    return unicode(bfsnr_result[0][0])

def get_gemname(config, bfsnr):
    
    gemname_sql = "select bfs_name from bfs where bfs_nr=" + bfsnr
    
    gemname_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], gemname_sql)
    
    return gemname_result[0][0]

def extract_ticket_from_legend_url(legend_url):
    
    url_path = urlparse.urlsplit(legend_url)[2]
    
    ticket = url_path.split("/")[2]
    
    return ticket
    

def get_legend_path(config, liefereinheit):
    
    legend_path_sql = "select distinct EIB_LEGENDESYMBOL_DE from eigentumsbeschraenkung where eib_liefereinheit=" + liefereinheit
    
    legend_path_sql_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_VEK1']['connection_string'], legend_path_sql)
    
    legend_path = ""
    tickets = []
    
    for lp in legend_path_sql_result:
        legend_url = lp[0]
        
        ticket = extract_ticket_from_legend_url(legend_url)
        tickets.append(ticket)
    
    unique_tickets = list(set(tickets))
    if len(unique_tickets) == 1:
        legend_path = os.path.join(config['GENERAL']['files_be_ch_baseunc'], liefereinheit, unique_tickets[0], "legenden")
    else:
        sys.exit()
    
    return legend_path
    
def run_create_legend(input_bfsnr):
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    
    liefereinheiten = get_liefereinheiten(config, input_bfsnr)
    
    if len(liefereinheiten) == 0:
        logger.error("Für die gewünschte BFSNR " + unicode(input_bfsnr) + " wurden in VEK1 keine Daten gefunden.")
        logger.error("Script wird abgebrochen.")
        sys.exit()
    
    for liefereinheit in liefereinheiten:
        bfsnr = get_bfsnr(config, liefereinheit)
        gemname = get_gemname(config, bfsnr)
        legend_path = get_legend_path(config, liefereinheit)
        if not os.path.exists(legend_path):
            os.makedirs(legend_path)
        logger.info("Erstelle Legenden für Liefereinheit " + liefereinheit + "(" + gemname + "/" + bfsnr + ")")
        logger.info("UNC-Pfad für Legenden: " + legend_path)
    
    logger.info("Legenden werden erstellt.")

