# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects
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

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgef�hrt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    token = "0"
    # Das Legendenverzeichnis muss im Voraus vorhanden sein, damit der HTTP-Fetcher
    # im FME dorthin schreiben kann. Er erzeugt keine Directories.
    if not os.path.exists(legend_basedir):
        os.makedirs(legend_basedir)
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"
    if config['LEGENDS']['use_token_auth'] == "1":
        token = getToken(config['LEGENDS']['username'], config['LEGENDS']['password'], config['LEGENDS']['get_token_url'])
        mapservice_legend_url = config['LEGENDS']['legend_mapservice_base_url'] + config['LEGENDS']['legend_mapservice_name'] + "/MapServer/legend?f=json&pretty=true&token=" + token
    else:
        mapservice_legend_url = config['LEGENDS']['legend_mapservice_base_url'] + config['LEGENDS']['legend_mapservice_name'] + "/MapServer/legend?f=json&pretty=true"
    logger.info("Verwende folgende REST-URL für Legendenbilder:")
    logger.info(mapservice_legend_url)
    
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
        'MAPSERVICE_BASE_URL': str(config['LEGENDS']['legend_mapservice_base_url']),
        'MAPSERVICE_LEGEND_URL': str(mapservice_legend_url),
        'MAPSERVICE_NAME': str(config['LEGENDS']['legend_mapservice_name']),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LEGEND_BASEDIR': str(legend_basedir),
        'TOKEN': str(token),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
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
    
