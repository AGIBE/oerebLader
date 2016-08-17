# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import datetime
import codecs
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import jinja2
import cx_Oracle

logger = logging.getLogger('oerebLaderLogger')

def get_legend_entries(config):
    legend_sql = "select distinct CAST(eib_aussage_de AS NVARCHAR2(1000)) aussage, eib_legendesymbol_de, eib_liefereinheit, eib_sort from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + unicode(config['LIEFEREINHEIT']['id']) + " order by eib_sort"
    legend_list = []
    
    legends = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], legend_sql)
    
    for legend in legends:
        legend_dict = {
            "label": legend[0],
            'symbol': legend[1]
        }
        legend_list.append(legend_dict)

    return legend_list
        

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")

    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    gemname = config['LIEFEREINHEIT']['gemeinde_name']
    logger.info("Die Legende für die Gemeinde " + unicode(bfsnr) + " wird erstellt.")

    legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    if not os.path.exists(legend_dir):
        os.makedirs(legend_dir)
    html_filename = os.path.join(legend_dir, "legende_komplett.html") 
    templateLoader = jinja2.FileSystemLoader(searchpath=config['GENERAL']['legend_template_dir'])
    templateEnv = jinja2.Environment( loader=templateLoader )
    
    TEMPLATE_FILE = "legend_template.txt"
    template = templateEnv.get_template( TEMPLATE_FILE )
    
    # Here we add a new input variable containing a list.
    # Its contents will be expanded in the HTML as a unordered list.
    FAVORITES = [ "chocolates", "lunar eclipses", "rabbits" ]
    legend_entries = get_legend_entries(config)
    
    templateVars = { "gemname" : gemname,
                     "legend_entries" : legend_entries
                   }
    
    outputText = template.render(templateVars)
    with codecs.open(html_filename, "w", "utf8") as html_file:
        html_file.write(outputText)
    
    logger.info("Legende wurde in " + html_filename + " geschrieben.")
    
