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
    legend_sql = "select distinct CAST(eib_aussage_de AS NVARCHAR2(1000)) aussage_de, eib_legendesymbol_de, CAST(eib_aussage_fr AS NVARCHAR2(1000)) aussage_fr, eib_legendesymbol_fr, eib_liefereinheit, eib_sort from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + unicode(config['LIEFEREINHEIT']['id']) + " order by eib_sort asc, aussage_de asc"
    legend_list = []
    
    legends = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], legend_sql)
    
    for legend in legends:
        legend_dict = {
            "label_de": legend[0],
            'symbol_de': legend[1],
            "label_fr": legend[2],
            'symbol_fr': legend[3]
        }
        legend_list.append(legend_dict)

    return legend_list

def render_template(config, template_file, templateVars, html_filename):
    templateLoader = jinja2.FileSystemLoader(searchpath=config['LEGENDS']['legend_template_dir'])
    templateEnv = jinja2.Environment( loader=templateLoader )
    template = templateEnv.get_template(template_file)

    outputText = template.render(templateVars)
    with codecs.open(html_filename, "w", "utf8") as html_file:
        html_file.write(outputText)    

def create_legend_npl(config, legend_dir, gemname):
    
    html_filename_de = os.path.join(legend_dir, unicode(config['LIEFEREINHEIT']['bfsnr']) + "_legende_npl_de.html")
    html_filename_fr = os.path.join(legend_dir, unicode(config['LIEFEREINHEIT']['bfsnr']) + "_legende_npl_fr.html")
    
    template_filename_de = "legend_npl_template_de.txt"
    template_filename_fr = "legend_npl_template_fr.txt"
    
    legend_entries = get_legend_entries(config)
    template_vars = { "gemname" : gemname,
                     "legend_entries" : legend_entries
                   }
    
    # Deutsch
    render_template(config, template_filename_de, template_vars, html_filename_de)
        
    # Französisch
    render_template(config, template_filename_fr, template_vars, html_filename_fr)
    

def create_legend_komplett(config, legend_dir, gemname):
    
    html_filename_de = os.path.join(legend_dir, unicode(config['LIEFEREINHEIT']['bfsnr']) + "_legende_komplett_de.html") 
    html_filename_fr = os.path.join(legend_dir, unicode(config['LIEFEREINHEIT']['bfsnr']) + "_legende_komplett_fr.html")

    template_filename_de = "legend_komplett_template_de.txt"
    template_filename_fr = "legend_komplett_template_fr.txt"

    legend_entries = get_legend_entries(config)
#     subthemes = get_subthemes(config)
    
    template_vars = { "gemname" : gemname,
                     "legend_entries" : legend_entries
                   }

    # Deutsch
    render_template(config, template_filename_de, template_vars, html_filename_de)
        
    # Französisch
    render_template(config, template_filename_fr, template_vars, html_filename_fr)

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")

    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    gemname = config['LIEFEREINHEIT']['gemeinde_name']
    logger.info("Die Legende für die Gemeinde " + unicode(bfsnr) + " wird erstellt.")

    legend_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    if not os.path.exists(legend_dir):
        os.makedirs(legend_dir)
    logger.info("Die Legenden werden abgelegt in: " + legend_dir)
        
    create_legend_npl(config, legend_dir, gemname)
    logger.info("NPL-Legenden (de/fr) wurden erstellt")
    
    create_legend_komplett(config, legend_dir, gemname)
    logger.info("Komplette Gemeinde-Legenden (de/fr) wurden erstellt")
    
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
