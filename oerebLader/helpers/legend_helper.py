# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import jinja2
import codecs
import oerebLader.helpers.sql_helper

logger = logging.getLogger('oerebLaderLogger')


def get_legend_entries(connection_string, liefereinheit):
    legend_sql = "select distinct CAST(eib_aussage_de AS NVARCHAR2(1000)) aussage_de, eib_legendesymbol_de, CAST(eib_aussage_fr AS NVARCHAR2(1000)) aussage_fr, eib_legendesymbol_fr, eib_liefereinheit, eib_sort from EIGENTUMSBESCHRAENKUNG where eib_liefereinheit=" + unicode(liefereinheit) + " order by eib_sort asc, aussage_de asc"
    legend_list = []
    
    legends = oerebLader.helpers.sql_helper.readSQL(connection_string, legend_sql)
    
    for legend in legends:
        legend_dict = {
            "label_de": legend[0],
            'symbol_de': legend[1],
            "label_fr": legend[2],
            'symbol_fr': legend[3]
        }
        legend_list.append(legend_dict)

    return legend_list

def render_template(template_path, template_file, templateVars, html_filename):
    templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
    templateEnv = jinja2.Environment( loader=templateLoader )
    template = templateEnv.get_template(template_file)

    outputText = template.render(templateVars)
    with codecs.open(html_filename, "w", "utf8") as html_file:
        html_file.write(outputText)    

def create_legends(legend_dir, gemname, bfsnr, liefereinheit, connection_string, template_path):
    
    html_npl_filename_de = os.path.join(legend_dir, unicode(bfsnr) + "_legende_npl_de.html")
    html_npl_filename_fr = os.path.join(legend_dir, unicode(bfsnr) + "_legende_npl_fr.html")

    html_komplett_filename_de = os.path.join(legend_dir, unicode(bfsnr) + "_legende_komplett_de.html") 
    html_komplett_filename_fr = os.path.join(legend_dir, unicode(bfsnr) + "_legende_komplett_fr.html")

    npl_template_filename_de = "legend_npl_template_de.txt"
    npl_template_filename_fr = "legend_npl_template_fr.txt"

    komplett_template_filename_de = "legend_komplett_template_de.txt"
    komplett_template_filename_fr = "legend_komplett_template_fr.txt"
    
    legend_entries = get_legend_entries(connection_string, liefereinheit)
    template_vars = { "gemname" : gemname,
                     "legend_entries" : legend_entries
                   }
    # Deutsch
    render_template(template_path, npl_template_filename_de, template_vars, html_npl_filename_de)
    render_template(template_path, komplett_template_filename_de, template_vars, html_komplett_filename_de)
        
    # Französisch
    render_template(template_path, npl_template_filename_fr, template_vars, html_npl_filename_fr)
    render_template(template_path, komplett_template_filename_fr, template_vars, html_komplett_filename_fr)
