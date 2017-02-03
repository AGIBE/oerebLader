# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import logging
import os
import fmeobjects
import sys
import requests

logger = logging.getLogger('oerebLaderLogger')

def getToken(username, password, tokenURL):
    token = ""

    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json'}
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    res = requests.post(tokenURL, data=params, headers=headers)
    
    if res.status_code == 200:
        if 'token' in res.json():
            token = res.json()['token']
        else:
            logger.error("Es konnte kein Token erezugt werden!")
            logger.error("Import wird abgebrochen!")
            sys.exit()
    else:
        logger.error("Es konnte kein Token erezugt werden!")
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    return token

def getWMSLayers(wms_rest_url, bfsnr):
    result_layers = "keine Layer mit gemeindespezifischer Darstellung gefunden."
    req = requests.get(wms_rest_url)
    json_result = req.json()
    layers = []
    
    for layer in json_result['layers']:
        if layer['name'].endswith("_" + unicode(bfsnr)):
            layers.append(layer['name'])
    
    if len(layers) > 0:
            result_layers = ",".join(layers) 
    
    return result_layers

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgef�hrt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    token = ""
    runner = fmeobjects.FMEWorkspaceRunner()
    bfsnr = config['LIEFEREINHEIT']['bfsnr']

    if config['LEGENDS']['use_token_auth'] == "1":
        token = getToken(config['LEGENDS']['username'], config['LEGENDS']['password'], config['LEGENDS']['get_token_url'])
        mapservice_layer_url = config['LEGENDS']['legend_mapservice_base_url'] + config['LEGENDS']['legend_mapservice_name'] + "/MapServer?f=json&pretty=true&token=" + token
    else:
        mapservice_layer_url = config['LEGENDS']['legend_mapservice_base_url'] + config['LEGENDS']['legend_mapservice_name'] + "/MapServer?f=json&pretty=true"
    logger.info("Verwende folgende REST-URL für Layerinfos:")
    logger.info(mapservice_layer_url)
    
    wms_layers = getWMSLayers(mapservice_layer_url, bfsnr)
    logger.info("Folgende WMS-Layer werden berücksichtigt.")
    logger.info(wms_layers)
    
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    else:
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    #TODO: Parameter für Sprache der Gemeinde einbauen und GEGR entsprechend abfüllen
    parameters = {
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'GEODB_DATABASE': str(config['GEODB_WORK']['database']),
        'GEODB_USERNAME': str(config['GEODB_WORK']['username']),
        'GEODB_PASSWORD': str(config['GEODB_WORK']['password']),
        'GDBV_DATABASE': str(config['GDBV_WORK']['database']),
        'GDBV_USERNAME': str(config['GDBV_WORK']['username']),
        'GDBV_PASSWORD': str(config['GDBV_WORK']['password']),
        'BFSNR': str(bfsnr),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),        
        'WMS_LAYERS': wms_layers,
        'NPL_WMS_BASE': str(config['GENERAL']['npl_wms_base']),
        'MAPSERVICE_NAME': str(config['LEGENDS']['legend_mapservice_name']),
        'OUTPUT_RV_URL': str(output_rv_url),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")