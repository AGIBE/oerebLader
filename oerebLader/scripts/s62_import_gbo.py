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
    # os.path.dirname wird benötigt, weil in gpr_source die MDB enthalten ist.
    input_rv_dir = os.path.join(os.path.dirname(config['LIEFEREINHEIT']['gpr_source']), "rv")
    output_rv_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']))
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    else:
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
    excel_file_amt = os.path.join(config['LIEFEREINHEIT']['ts_source'], "AMT_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    excel_file_darstellungsdienst = os.path.join(config['LIEFEREINHEIT']['ts_source'], "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/GBO/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/GBO/"

    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'WORK_CONNECTION': str(config['GEODB_WORK']['connection_file']),
        'OEREB2_DATABASE': str(config['OEREB2_WORK']['database']),
        'OEREB2_USERNAME': str(config['OEREB2_WORK']['username']),
        'OEREB2_PASSWORD': str(config['OEREB2_WORK']['password']),
        'OEREB2_CONNECTION': str(config['OEREB2_WORK']['connection_file']),
        'GEODB_PG_DATABASE': str(config['GEODB_WORK_PG']['database']),
        'GEODB_PG_USERNAME': str(config['GEODB_WORK_PG']['username']),
        'GEODB_PG_PASSWORD': str(config['GEODB_WORK_PG']['password']),
        'GEODB_PG_HOST': str(config['GEODB_WORK_PG']['host']),
        'GEODB_PG_PORT': str(config['GEODB_WORK_PG']['port']),
        'FGDB': str(config['LIEFEREINHEIT']['gpr_source']),
        'INPUT_RV_DIR': str(input_rv_dir),
        'OUTPUT_RV_DIR': str(output_rv_dir),
        'OUTPUT_RV_URL': str(output_rv_url),
        'EXCEL_DARSTELLUNGSDIENST': str(excel_file_darstellungsdienst),
        'EXCEL_AMT': str(excel_file_amt),
        'LEGEND_BASEURL': str(legend_baseurl),
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

