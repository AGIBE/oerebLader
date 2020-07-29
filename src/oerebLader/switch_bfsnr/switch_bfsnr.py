# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import codecs
import datetime
import logging
import mappyfile
import oerebLader.logging
import oerebLader.mapfile

def run_switch_bfsnr(bfsnr):
    mode = "oerebpruef_gemeinde"
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("switch_bfsnr", config)
    logger.info("Die BFS-Nummer im Gemeinde-Prüfdienst wird gewechselt auf: " + unicode(bfsnr))
    
    repo_dir = os.environ["OEREB_REPO_PRUEF"]
    layers = []
    for layer in config['KOMMUNALE_LAYER']:
        layers.append(layer['layer'])
#         layers.append(layer['layer'].split(".")[1])

    search_string = "[[[BFSNR]]]"
    bfsnr = unicode(bfsnr)
    template_mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef.map")
    
    filter_string = " and bfsnr=" + bfsnr
    
    mapfile_path = os.path.join(repo_dir, "oerebpruef/oerebpruef_gemeinde.map")

    logger.info("Template Mapfile öffnen: " + template_mapfile_path)
    with codecs.open(template_mapfile_path, "r", encoding="utf-8") as template_mapfile:
        template_content = template_mapfile.read()
    
    logger.info("Filter-String ersetzen mit: " + filter_string)
    template_content = template_content.replace(search_string, filter_string)
    
#     for layer in layers:
#         layer_search_string = "###" + layer + "###"
#         layer_replace_string = 'INCLUDE "nupla/' + bfsnr + '/' + layer + '_' + bfsnr + '.map"'
#         logger.info("Layer-String ersetzen: " + layer_replace_string)
#         template_content = template_content.replace(layer_search_string, layer_replace_string)
    
    logger.info("Gemeinde-Mapfile schreiben: " + mapfile_path)
    with codecs.open(mapfile_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(template_content)
        
    logger.info("Gemeinde-Mapfile wird mit mappyfile geparst: " + mapfile_path)
    mf_content = mappyfile.open(mapfile_path, expand_includes=True)
    
    # Sprachunabhängige Parameter manipulieren
    
    # Stufe MAP
    mf_content = oerebLader.mapfile.fill_map_metadata(mf_content, mode, config)
    
    # Stufe LAYER
    mf_content = oerebLader.mapfile.fill_layer_metadata(mf_content, mode, config)
        
    # Sprachabhängige Parameter manipulieren

    # Stufe MAP
    mf_content = oerebLader.mapfile.fill_map_language_metadata(mf_content, "de", mode, config)
    
    # Stufe LAYER
    mf_content = oerebLader.mapfile.fill_layer_language_metadata(mf_content, "de", config)
    
    # Gemeindespezifische Mapfiles includen
    # Damit der Include am Beginn, d.h. vor den kantonalen Symbolen
    # eingefügt wird, muss er mit mappyfile.insert eingefügt werden.
    # Da aber ein Einzeiler-Include von mappyfile nicht geparst werden kann
    # (s. https://github.com/geographika/mappyfile/issues/39), muss eine Fake-
    # CLASS gebildet werden. 
    for layer in layers:
        layername_without_prefix = layer.split(".")[1]
        include_string = '''
        CLASS
            INCLUDE "nupla/%s/%s_%s.map"
        END
        ''' % (bfsnr, layername_without_prefix, bfsnr)
        new_include = mappyfile.loads(include_string, expand_includes=False)
        mf_layer = mappyfile.find(mf_content['layers'], 'name', layer)
        mf_layer['classes'].insert(0, new_include)
        
    mf_dumped = mappyfile.dumps(mf_content)
    
    # Die Fake-CLASS wird im Anschluss im gedumpten String durch das effektive 
    # Include ersetzt. Es wird vor und nach dem Include ein newline eingefügt,
    # damit das Include sicher auf einer neuen, eigenen Zeile landet.
    for layer in layers:
        layername_without_prefix = layer.split(".")[1]
        include_string = '''
        CLASS
            INCLUDE "nupla/%s/%s_%s.map"
        END
        ''' % (bfsnr, layername_without_prefix, bfsnr)
        include_line = '\nINCLUDE "nupla/%s/%s_%s.map"\n' % (bfsnr, layername_without_prefix, bfsnr)
        mf_dumped = mf_dumped.replace(include_string, include_line)
        
    logger.info("Gemeinde-Mapfile schreiben: " + mapfile_path)
    with codecs.open(mapfile_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(mf_dumped)
        
    logger.info("BFS-Nummer im Gemeinde-Prüfdienst wurde gewechselt auf: " + bfsnr)