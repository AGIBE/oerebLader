# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.fme
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.splitext(__file__)[0] + ".log")
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    itf_file = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), unicode(bfsnr) + ".itf")
    excel_file_amt = config['GENERAL']['amt_tabelle']
    excel_file_darstellung = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), "DARSTELLUNGSDIENST_" + unicode(bfsnr) + ".xlsx")
    input_rv_dir = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), "rv")
    input_legend_dir = os.path.join(config['LIEFEREINHEIT']['gpr_source'], unicode(bfsnr), unicode(config['ticketnr']), "legenden")
    output_rv_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    else:
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    if not os.path.exists(legend_basedir):
        os.makedirs(legend_basedir)
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"    
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
        'EXCEL_AMT': str(excel_file_amt),
        'EXCEL_DARSTELLUNG': str(excel_file_darstellung),
        'BFSNR': str(bfsnr),
        'GEMNAME': config['LIEFEREINHEIT']['gemeinde_name'].encode("latin-1"),
        'ITF_FILE': str(itf_file),
        'LIEFEREINHEIT': str(config['LIEFEREINHEIT']['id']),
        'NPL_WMS_BASE': str(config['GENERAL']['npl_wms_base']),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LEGEND_BASEDIR': str(legend_basedir),
        'LEGEND_INPUTDIR': str(input_legend_dir),
        'INPUT_RV_DIR': str(input_rv_dir),
        'OUTPUT_RV_DIR': str(output_rv_dir),
        'OUTPUT_RV_URL': str(output_rv_url),
        'CREATE_LINETABLES': str(config['GENERAL']['create_linetables']),
        'STROKER': str(config['GENERAL']['fme_stroker_value']),
        'AMT_OID': str(config['LIEFEREINHEIT']['amt_oid'])
    }

    fmerunner = AGILib.fme.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
