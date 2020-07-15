# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import jinja2
import codecs

logger = logging.getLogger('oerebLaderLogger')

def get_legend_subthemes(connection, liefereinheit, theme):
    subtheme_list = []
    subtheme_sql = "select distinct eib.STH_ID, sth.STH_NAME_DE, sth.STH_NAME_FR, sth.STH_SORT, the.the_sort from EIGENTUMSBESCHRAENKUNG eib LEFT JOIN SUBTHEMA sth ON eib.STH_ID=sth.STH_ID LEFT JOIN THEMA the ON sth.THE_ID=the.THE_ID where eib_liefereinheit=" + unicode(liefereinheit) + " and sth.THE_ID=" + unicode(theme) + " order by the.the_sort, sth.sth_sort"

    subthemes = connection.db_read(subtheme_sql)

    for subtheme in subthemes:
        subtheme_dict = {
            "sth_id": subtheme[0],
            "sth_name_de": subtheme[1],
            "sth_name_fr": subtheme[2],
            "sth_sort": subtheme[3],
            "legend_entries": get_legend_entries(connection, liefereinheit, subtheme[0])
        }
        subtheme_list.append(subtheme_dict)

    return subtheme_list

def get_legend_themes(connection, liefereinheit):
    theme_list = []
    themes_sql = "select distinct sth.THE_ID, the.THE_NAME_DE, the.THE_NAME_FR, the.THE_SORT from EIGENTUMSBESCHRAENKUNG eib LEFT JOIN SUBTHEMA sth ON eib.STH_ID=sth.STH_ID LEFT JOIN THEMA the ON sth.THE_ID=the.THE_ID where eib_liefereinheit=" + unicode(liefereinheit) + " order by the.the_sort asc"

    themes = connection.db_read(themes_sql)

    for theme in themes:
        theme_dict = {
            "the_id": theme[0],
            "the_name_de": theme[1],
            "the_name_fr": theme[2],
            "the_sort": theme[3],
            "subthemes": get_legend_subthemes(connection, liefereinheit, theme[0])
        }

        theme_list.append(theme_dict)

    return theme_list

def get_legend_entries(connection, liefereinheit, subtheme):
    legend_sql = "select distinct CAST(eib_aussage_de AS NVARCHAR2(1000)) aussage_de, eib_legendesymbol_de, CAST(eib_aussage_fr AS NVARCHAR2(1000)) aussage_fr, eib_legendesymbol_fr, eib_liefereinheit, eib_sort from EIGENTUMSBESCHRAENKUNG eib LEFT JOIN SUBTHEMA sth ON eib.STH_ID=sth.STH_ID LEFT JOIN THEMA the ON sth.THE_ID=the.THE_ID where eib_liefereinheit=" + unicode(liefereinheit) + " and eib.STH_ID=" + unicode(subtheme) + " order by eib_sort asc, aussage_de asc"
    legend_list = []
    
    legends = connection.db_read(legend_sql)
    
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

def create_legends(legend_dir, gemname, bfsnr, liefereinheit, connection, template_path):
    
    html_npl_filename_de = os.path.join(legend_dir, unicode(bfsnr) + "_legende_npl_de.html")
    html_npl_filename_fr = os.path.join(legend_dir, unicode(bfsnr) + "_legende_npl_fr.html")

    html_komplett_filename_de = os.path.join(legend_dir, unicode(bfsnr) + "_legende_komplett_de.html") 
    html_komplett_filename_fr = os.path.join(legend_dir, unicode(bfsnr) + "_legende_komplett_fr.html")

    npl_template_filename_de = "legend_npl_template_de.txt"
    npl_template_filename_fr = "legend_npl_template_fr.txt"

    komplett_template_filename_de = "legend_komplett_template_de.txt"
    komplett_template_filename_fr = "legend_komplett_template_fr.txt"
    
    themes = get_legend_themes(connection, liefereinheit)
    template_vars = { "gemname" : gemname,
                     "themes" : themes
                   }
    # Deutsch
    render_template(template_path, npl_template_filename_de, template_vars, html_npl_filename_de)
    render_template(template_path, komplett_template_filename_de, template_vars, html_komplett_filename_de)
        
    # Französisch
    render_template(template_path, npl_template_filename_fr, template_vars, html_npl_filename_fr)
    render_template(template_path, komplett_template_filename_fr, template_vars, html_komplett_filename_fr)
