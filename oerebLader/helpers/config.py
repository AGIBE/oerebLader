# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import configobj
import os
import tempfile
import arcpy
import logging
import datetime

def get_general_configfile_from_envvar():
    '''
    Holt den Pfad zur Konfigurationsdatei aus der Umgebungsvariable
    OEREBIMPORTHOME und gibt dann den vollständigen Pfad (inkl. Dateiname)
    der Konfigurationsdatei zurück.
    '''
    config_directory = os.environ['OEREBIMPORTHOME']
    config_filename = "config.ini"
    
    config_file = os.path.join(config_directory, config_filename)
    
    return config_file

def init_generalconfig():
    '''
    liest die zentrale Konfigurationsdatei in ein ConfigObj-Objet ein.
    Dieser kann wie ein Dictionary gelesen werden.
    '''
    config_filename = get_general_configfile_from_envvar()
    config_file = configobj.ConfigObj(config_filename, encoding="UTF-8")
    
    # Die Walk-Funktion geht rekursiv durch alle
    # Sections und Untersections der Config und 
    # ruft für jeden Key die angegebene Funktion
    # auf
    # config_file.walk(decrypt_passwords)
    
    return config_file.dict()

def create_connection_files(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    temp_directory = tempfile.mkdtemp()
    sde_filename = key + ".sde"
    connection_file = os.path.join(temp_directory, sde_filename)
    logging.info("Erzeuge Connectionfile " + connection_file)
    arcpy.CreateDatabaseConnection_management(temp_directory, sde_filename, "ORACLE", database, "DATABASE_AUTH", username, password ) 
    config[key]['connection_file'] = connection_file
    
def create_connection_string(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    connection_string = username + "/" + password + "@" + database
    config[key]['connection_string'] = connection_string
    
def init_logging(ticketnr, config):
    log_directory = os.path.join(config['LOGGING']['basedir'], unicode(ticketnr))
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, unicode(ticketnr) + ".log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = unicode(ticketnr) + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_config(ticketnr):
    config = init_generalconfig()
    
    init_logging(ticketnr, config)
    
    create_connection_string(config, 'GEODB_WORK')
    create_connection_string(config, 'OEREB_WORK')

    create_connection_files(config, 'GEODB_WORK')
    create_connection_files(config, 'OEREB_WORK')    

    return config