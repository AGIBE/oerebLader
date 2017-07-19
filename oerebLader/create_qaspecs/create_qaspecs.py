# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import datetime
import codecs
import oerebLader.helpers.log_helper
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper

def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "create_qaspecs")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "create_qaspecs.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "create_qaspecs" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    logger.info("Das Logfile heisst: " + logfile)
    
    return logger

def get_liefereinheiten(config):
    liefereinheiten_sql = "select id from liefereinheit order by id"
    liefereinheiten_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], liefereinheiten_sql)
    liefereinheiten = []
    for le in liefereinheiten_result:
        liefereinheiten.append(le[0])
    return liefereinheiten

def run_create_qaspecs(config=None, liefereinheiten=[-1]):
    if config is not None:
        logger = logging.getLogger('oerebLaderLogger')
    else:
        config = oerebLader.helpers.config.get_config()
        logger = init_logging(config)
    
    logger.info("Die QA-Spezifikationen werden neu erstellt.")
    
    qa_basedir = config['GENERAL']['qa']
    
    template2_qa_filename = os.path.join(qa_basedir, "OEREB2_Liefereinheit_Template.qa.xml")
    logger.info("Folgende Template-Files werden verwendet:")
    logger.info(template2_qa_filename)
    template2_qa = ""
    
    with codecs.open(template2_qa_filename, "r", "utf-8") as template2_qa_file:
        template2_qa = template2_qa_file.read()
    
    qa2_dir = os.path.join(qa_basedir, "OEREB2")
    logger.info("Die QA-Spezifikation werden gespeichert in: ")
    logger.info(qa2_dir)
    
    if liefereinheiten[0] == -1:
        liefereinheiten = get_liefereinheiten(config)
        
    for le in liefereinheiten:
        logger.info("Liefereinheit " + unicode(le) + " wird bearbeitet.")
        liefereinheit2_qa_filename = os.path.join(qa2_dir, "OEREB2_" + unicode(le) + ".qa.xml")
        template2_qa_liefereinheit = template2_qa.replace("$$$LIEFEREINHEIT$$$", unicode(le))

        logger.info("Datei " + liefereinheit2_qa_filename + " wird geschrieben.")
        with codecs.open(liefereinheit2_qa_filename, "w", "utf-8") as liefereinheit2_qa_file:
            liefereinheit2_qa_file.write(template2_qa_liefereinheit)
    
    logger.info("QA-Spezifikationen wurden erstellt.")
    