# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.agilogger
import os

def init_logging(command_name, config):
    logfile_folder = os.path.join(config['LOGGING']['basedir'], command_name)
    logfile_name = command_name + ".log"
    config['logging']['log_directory'] = logfile_folder
    logger = AGILib.agilogger.initialize_agilogger(logfile_name=logfile_name, logfile_folder=logfile_folder, list_log_handler=['file', 'stream'], archive=True, logger_name="oerebLaderLogger")
    return logger
