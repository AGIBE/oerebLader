# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import sys
import logging
import os
import fmeobjects

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw",".log"))
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)

    # os.path.dirname wird benötigt, weil in gpr_source die MDB enthalten ist.
    input_rv_dir = os.path.join(os.path.dirname(config['LIEFEREINHEIT']['gpr_source']), "rv")
    excel_file_teilplaene = os.path.join(os.path.dirname(config['LIEFEREINHEIT']['gpr_source']), "rv", "ListeTeilplaene.xlsx")
    output_rv_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
        output_plan_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/plan/"
    else:
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
        output_plan_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/plan/"
    excel_file_amt = config['GENERAL']['amt_tabelle']
    excel_file_darstellungsdienst = os.path.join(config['LIEFEREINHEIT']['ts_source'], "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/NSG/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/NSG/"
    
    output_plan_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), "plan")
    logger.info("Output-Dir Pläne: " + output_plan_dir)
    logger.info("Output-URL Pläne: " + output_plan_url)

    parameters = {
        'WORK_CONNECTION': config['GEODB_WORK']['connection_file'],
        'OEREB2_DATABASE': config['OEREB2_WORK']['database'],
        'OEREB2_USERNAME': config['OEREB2_WORK']['username'],
        'OEREB2_PASSWORD': config['OEREB2_WORK']['password'],
        'OEREB2_CONNECTION': config['OEREB2_WORK']['connection_file'],
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
        'FGDB': config['LIEFEREINHEIT']['gpr_source'],
        'INPUT_RV_DIR': input_rv_dir,
        'OUTPUT_RV_DIR': output_rv_dir,
        'OUTPUT_RV_URL': output_rv_url,
        'OUTPUT_PLAN_DIR': output_plan_dir,
        'OUTPUT_PLAN_URL': output_plan_url,
        'EXCEL_DARSTELLUNGSDIENST': excel_file_darstellungsdienst,
        'EXCEL_AMT': excel_file_amt,
        'EXCEL_TEILPLAENE': excel_file_teilplaene,
        'LEGEND_BASEURL': legend_baseurl,
        'LIEFEREINHEIT': unicode(config['LIEFEREINHEIT']['id']),
        'STROKER': unicode(config['GENERAL']['fme_stroker_value'])
    }

    fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
    fmerunner.run()
    if fmerunner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")

