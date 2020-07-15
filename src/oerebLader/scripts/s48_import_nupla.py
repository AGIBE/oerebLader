# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.fme_helper
import sys
import logging
import os
import fmeobjects
import json

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
    excel_file_amt = config['GENERAL']['amt_tabelle']
    simplify_geometry = config['GENERAL']['simplify_geometry']
    input_rv_dir = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), "rv")
    output_rv_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']))
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
        'EXCEL_AMT': str(excel_file_amt),
        'BFSNR': str(bfsnr),
        'GEMNAME': config['LIEFEREINHEIT']['gemeinde_name'].encode("latin-1"),
        'ITF_FILE': str(itf_file),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'INPUT_RV_DIR': str(input_rv_dir),
        'OUTPUT_RV_DIR': str(output_rv_dir),
        'OUTPUT_RV_URL': str(output_rv_url),
        'SIMPLIFY_GEOMETRY': str(simplify_geometry),
        'CREATE_LINETABLES': str(config['GENERAL']['create_linetables']),
        'STROKER': str(config['GENERAL']['fme_stroker_value']),
        'NPL_WMS_BASE': str(config['GENERAL']['npl_wms_base']),
        'AMT_OID': str(config['LIEFEREINHEIT']['amt_oid']),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
        
    # Alle Darstellungscodes, die mit S beginnen,
    # werden durch ein F ersetzt (s. #242)
    for layer in config['KOMMUNALE_LAYER']:
        logger.info("Französischsprachige Darstellungscodes werden übersetzt.")
        tablename = layer['table']
        logger.info("Tabelle " + tablename)
        darst_c_sql = "update " + tablename + " set darst_c = 'F' || substr(darst_c, 2) where darst_c like 'S%' and bfsnr=" + unicode(bfsnr)
        logger.info("Update Oracle-WORK...")
        config['GEODB_WORK']['connection'].db_read(darst_c_sql)
        logger.info("Update PostGIS-WORK...")
        config['GEODB_WORK_PG']['connection'].db_read(darst_c_sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    