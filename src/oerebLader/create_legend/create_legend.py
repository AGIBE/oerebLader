# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime
import sys
import urlparse
import oerebLader.logging
import oerebLader.config
import oerebLader.create_legend.legend

def get_liefereinheiten(config, bfsnr, connection):
    
    liefereinheiten_list = []
    
    # Wenn bfsnr=9999 werden alle Liefereinheiten abgefragt.
    # Wenn bfsnr einen Wert hat, wird nur diese Liefereinheit abgefragt.
    if bfsnr == "ALL":
        liefereinheiten_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit like '___01' order by eib_liefereinheit"
    else:
        liefereinheit = unicode(bfsnr) + "01"
        liefereinheiten_sql = "select distinct eib_liefereinheit from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + liefereinheit
        
    liefereinheiten_result = connection.db_read(liefereinheiten_sql)
    
    for row in liefereinheiten_result:
        liefereinheiten_list.append(unicode(row[0]))
        
    return liefereinheiten_list

def get_bfsnr(config, liefereinheit):
    bfsnr_sql = "select bfsnr from liefereinheit where id=" + unicode(liefereinheit)
    
    # Sucht immer in WORK, da die LIEFEREINHEIT-Tabelle nur dort existiert.
    bfsnr_result = config['OEREB_WORK_PG']['connection'].db_read(bfsnr_sql)
    return unicode(bfsnr_result[0][0])

def get_gemname(config, bfsnr):
    
    gemname_sql = "select bfs_name from bfs where bfs_nr=" + bfsnr
    
    # Sucht immer in VEK1, da die BFS-Tabelle nur dort und nicht in WORK nachgeführt wird.
    gemname_result = config['OEREB2_VEK1']['connection'].db_read(gemname_sql)
    
    return gemname_result[0][0]

def extract_ticket_from_legend_url(legend_url):
    
    url_path = urlparse.urlsplit(legend_url)[2]
    
    ticket = url_path.split("/")[2]
    
    return ticket
    

def get_legend_path(config, liefereinheit, connection):
    
    legend_path_sql = "select distinct EIB_LEGENDESYMBOL_DE from eigentumsbeschraenkung where eib_liefereinheit=" + liefereinheit
    
    legend_path_sql_result = connection.db_read(legend_path_sql)
    
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
    
def run_create_legend(input_bfsnr, mode):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("create_legend", config)

    # Je nach Modus wird in anderer DB nach den Bildern gesucht.    
    if mode == 'oereb':
        connection = config['OEREB2_VEK1']['connection']
    elif mode == 'oerebpruef':
        connection = config['OEREB2_WORK']['connection']
    
    liefereinheiten = get_liefereinheiten(config, input_bfsnr, connection)
    
    if len(liefereinheiten) == 0:
        logger.error("Für die gewünschte BFSNR " + unicode(input_bfsnr) + " wurden in VEK1 keine Daten gefunden.")
        logger.error("Script wird abgebrochen.")
        sys.exit()
    
    for liefereinheit in liefereinheiten:
        bfsnr = get_bfsnr(config, liefereinheit)
        gemname = get_gemname(config, bfsnr)
        legend_path = get_legend_path(config, liefereinheit, connection)
        if not os.path.exists(legend_path):
            os.makedirs(legend_path)
        logger.info("Erstelle Legenden für Liefereinheit " + liefereinheit + "(" + gemname + "/" + bfsnr + ")")
        oerebLader.create_legend.legend.create_legends(legend_path, gemname, bfsnr, liefereinheit, connection, config['LEGENDS']['legend_template_dir'])
        logger.info("UNC-Pfad für Legenden: " + legend_path)
    
    logger.info("Legenden werden erstellt.")

