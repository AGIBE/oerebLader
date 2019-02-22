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
        output_objbl_url = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/objbl/"
    else:
        output_rv_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/"
        output_objbl_url = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/objbl/"
    excel_file_amt = os.path.join(config['LIEFEREINHEIT']['ts_source'], "AMT_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    excel_file_darstellungsdienst = os.path.join(config['LIEFEREINHEIT']['ts_source'], "DARSTELLUNGSDIENST_" + unicode(config['LIEFEREINHEIT']['id']) + ".xlsx")
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_fullurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/GGO/ggo.png"
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "legenden/GGO/"
    else:
        legend_fullurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/GGO/ggo.png"
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/legenden/GGO/"

    input_objbl_dir = os.path.join(os.path.dirname(config['LIEFEREINHEIT']['gpr_source']), "Objektblaetter")
    output_objbl_dir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "objbl")
    logger.info("Output-Dir Pläne: " + output_objbl_dir)
    logger.info("Output-URL Objektblätter: " + output_objbl_url)

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
        'OEREB_PG_DATABASE': str(config['OEREB_WORK_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_WORK_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_WORK_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_WORK_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_WORK_PG']['port']),
        'FGDB': str(config['LIEFEREINHEIT']['gpr_source']),
        'INPUT_RV_DIR': str(input_rv_dir),
        'OUTPUT_RV_DIR': str(output_rv_dir),
        'OUTPUT_RV_URL': str(output_rv_url),
        'INPUT_OBJBL_DIR': str(input_objbl_dir),
        'OUTPUT_OBJBL_DIR': str(output_objbl_dir),
        'OUTPUT_OBJBL_URL': str(output_objbl_url),
        'EXCEL_DARSTELLUNGSDIENST': str(excel_file_darstellungsdienst),
        'EXCEL_AMT': str(excel_file_amt),
        'LEGEND_BASEURL': str(legend_baseurl),
        'LEGEND_FULLURL': str(legend_fullurl),
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

