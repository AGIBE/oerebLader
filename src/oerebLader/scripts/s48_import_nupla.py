# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.fme
import sys
import logging
import os
import json

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw",".log"))
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
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

    parameters = {
        'OEREB2_DATABASE': config['OEREB2_WORK']['database'],
        'OEREB2_USERNAME': config['OEREB2_WORK']['username'],
        'OEREB2_PASSWORD': config['OEREB2_WORK']['password'],
        'GEODB_DATABASE': config['GEODB_WORK']['database'],
        'GEODB_USERNAME': config['GEODB_WORK']['username'],
        'GEODB_PASSWORD': config['GEODB_WORK']['password'],
        'GEODB_PG_DATABASE': config['GEODB_WORK_PG']['database'],
        'GEODB_PG_USERNAME': config['GEODB_WORK_PG']['username'],
        'GEODB_PG_PASSWORD': config['GEODB_WORK_PG']['password'],
        'GEODB_PG_HOST': config['GEODB_WORK_PG']['host'],
        'GEODB_PG_PORT': unicode(config['GEODB_WORK_PG']['port']),
        'OEREB_PG_DATABASE': config['OEREB_WORK_PG']['database'],
        'OEREB_PG_USERNAME': config['OEREB_WORK_PG']['username'],
        'OEREB_PG_PASSWORD': config['OEREB_WORK_PG']['password'],
        'OEREB_PG_HOST': config['OEREB_WORK_PG']['host'],
        'OEREB_PG_PORT': unicode(config['OEREB_WORK_PG']['port']),
        'MODELLABLAGE': config['GENERAL']['models'],
        'EXCEL_AMT': excel_file_amt,
        'BFSNR': unicode(bfsnr),
        'GEMNAME': config['LIEFEREINHEIT']['gemeinde_name'],
        'ITF_FILE': itf_file,
        'LIEFEREINHEIT': unicode(config['LIEFEREINHEIT']['id']),
        'INPUT_RV_DIR': input_rv_dir,
        'OUTPUT_RV_DIR': output_rv_dir,
        'OUTPUT_RV_URL': output_rv_url,
        'SIMPLIFY_GEOMETRY': simplify_geometry,
        'CREATE_LINETABLES': config['GENERAL']['create_linetables'],
        'STROKER': unicode(config['GENERAL']['fme_stroker_value']),
        'NPL_WMS_BASE': config['GENERAL']['npl_wms_base'],
        'AMT_OID': config['LIEFEREINHEIT']['amt_oid']
    }

    fmerunner = AGILib.fme.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    # Alle Darstellungscodes, die mit S beginnen,
    # werden durch ein F ersetzt (s. #242)
    for layer in config['KOMMUNALE_LAYER']:
        logger.info("Französischsprachige Darstellungscodes werden übersetzt.")
        tablename = layer['table']
        logger.info("Tabelle " + tablename)
        darst_c_sql = "update " + tablename + " set darst_c = 'F' || substr(darst_c, 2) where darst_c like 'S%' and bfsnr=" + unicode(bfsnr)
        logger.info("Update Oracle-WORK...")
        config['GEODB_WORK']['connection'].db_write(darst_c_sql)
        logger.info("Update PostGIS-WORK...")
        config['GEODB_WORK_PG']['connection'].db_write(darst_c_sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
