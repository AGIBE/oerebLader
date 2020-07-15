# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import datetime

def pad_string(string_to_pad):
    string_to_pad = '"' + string_to_pad + '"'
    return string_to_pad

def fill_map_metadata(mf, mode, config):

    mf['name'] = pad_string(mode)
    mf['web']['metadata']['"wms_srs"'] = pad_string(config['MAPFILE']['wms_srs'])
    mf['web']['metadata']['"wms_extent"'] = pad_string(config['MAPFILE']['wms_extent'])

    return mf

def fill_layer_metadata(mf, mode, config):

    for mapfile_layer in mf['layers']:
        mapfile_layer['connectiontype'] = config['MAPFILE']['CONNECTIONTYPE']
        mapfile_layer['connection'] = pad_string(config['MAPFILE']['CONNECTION'][mode])
        mapfile_layer['METADATA']['"wms_srs"'] = pad_string(config['MAPFILE']['wms_srs'])
        mapfile_layer['METADATA']['"wms_extent"'] = pad_string(config['MAPFILE']['wms_extent'])

    return mf

def fill_map_language_metadata(mf, lang, mode, config):
    wms_date = datetime.datetime.now().strftime("v%d.%m.%Y")
    wms_abstract = pad_string(config['MAPFILE']['wms_abstract'][mode][lang])
    wms_abstract = wms_abstract.replace('[[[DATE]]]', wms_date)
    
    mf['web']['metadata']['"wms_onlineresource"'] = pad_string(config['MAPFILE']['wms_onlineresource'][mode][lang])
    mf['web']['metadata']['"wms_title"'] = pad_string(config['MAPFILE']['wms_title'][mode][lang])
    mf['web']['metadata']['"wms_abstract"'] = wms_abstract
    mf['web']['metadata']['"wms_contactorganization"'] = pad_string(config['MAPFILE']['wms_contactorganization'][lang])
    mf['web']['metadata']['"wms_accessconstraints"'] = pad_string(config['MAPFILE']['wms_accessconstraints'][lang])
    
    return mf

def fill_layer_language_metadata(mf, lang, config):
    
    for mapfile_layer in mf['layers']:
        mapfile_layer_name = mapfile_layer['NAME'].strip('"')
        for param in config['MAPFILE']['LAYERS'][mapfile_layer_name]:
            value = config['MAPFILE']['LAYERS'][mapfile_layer_name][param][lang]
            param = pad_string(param)
            mapfile_layer['METADATA'][param] = pad_string(value)
    
    return mf

