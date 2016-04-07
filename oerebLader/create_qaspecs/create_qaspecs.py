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
    liefereinheiten = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], liefereinheiten_sql)
    return liefereinheiten

def run_create_qaspecs():
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Die QA-Spezifikationen aller Liefereinheiten werden neu erstellt.")
    
    qa_basedir = config['GENERAL']['qa']
    
    template_qa_filename = os.path.join(qa_basedir, "OEREB_Liefereinheit_Template.qa.xml")
    logger.info("Folgendes Template-File wird verwendet:")
    logger.info(template_qa_filename)
    template_qa = ""
    
    with codecs.open(template_qa_filename, "r", "utf-8") as template_qa_file:
        template_qa = template_qa_file.read() 
    
    qa_dir = os.path.join(qa_basedir, "OEREB")
    logger.info("Die QA-Spezifikation werden gespeichert in: ")
    logger.info(qa_dir)   
    
    for le in get_liefereinheiten(config):
        logger.info("Liefereinheit " + unicode(le[0]) + " wird bearbeitet.")
        liefereinheit_qa_filename = os.path.join(qa_dir, "OEREB_" + unicode(le[0]) + ".qa.xml")
        template_qa_liefereinheit = template_qa.replace("$$$LIEFEREINHEIT$$$", unicode(le[0]))
        logger.info("Datei " + liefereinheit_qa_filename + " wird geschrieben.")
        with codecs.open(liefereinheit_qa_filename, "w", "utf-8") as liefereinheit_qa_file:
            liefereinheit_qa_file.write(template_qa_liefereinheit)
    
    logger.info("QA-Spezifikationen wurden erstellt.")
    