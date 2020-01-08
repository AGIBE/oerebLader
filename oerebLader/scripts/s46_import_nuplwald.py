# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    runner = fmeobjects.FMEWorkspaceRunner()
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    itf_file = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), unicode(bfsnr) + ".itf")
    input_rv_dir = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), "rv")
    output_rv_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/Waldgrenzen/Waldgrenzen.png"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/Waldgrenzen/Waldgrenzen.png"
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
        'GEODB_PG_DATABASE': str(config['GEODB_WORK_PG']['database']),
        'GEODB_PG_USERNAME': str(config['GEODB_WORK_PG']['username']),
        'GEODB_PG_PASSWORD': str(config['GEODB_WORK_PG']['password']),
        'GEODB_PG_HOST': str(config['GEODB_WORK_PG']['host']),
        'GEODB_PG_PORT': str(config['GEODB_WORK_PG']['port']),
        'OEREB_PG_DATABASE': str(config['OEREB_WORK_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_WORK_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_WORK_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_WORK_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_WORK_PG']['port']),
        'MODELLABLAGE': str(config['GENERAL']['models']),
        'BFSNR': str(bfsnr),
        'GEMNAME': config['LIEFEREINHEIT']['gemeinde_name'].encode("latin-1"),
        'ITF_FILE': str(itf_file),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'INPUT_RV_DIR': str(input_rv_dir),
        'OUTPUT_RV_DIR': str(output_rv_dir),
        'OUTPUT_RV_URL': str(output_rv_url),
        'STROKER': str(config['GENERAL']['fme_stroker_value']),
        'WALDGRENZEN_VERFUEGUNG_DE': str(config['GENERAL']['waldgrenzen_verfuegung_de']),
        'WALDGRENZEN_VERFUEGUNG_FR': str(config['GENERAL']['waldgrenzen_verfuegung_fr']),
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
    
