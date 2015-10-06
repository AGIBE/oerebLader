# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import configobj
import os
import tempfile
import arcpy

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
    arcpy.CreateDatabaseConnection_management(temp_directory, sde_filename, "ORACLE", database, "DATABASE_AUTH", username, password ) 
    config[key]['connection_file'] = connection_file

def get_config():
    config = init_generalconfig()

    create_connection_files(config, 'GEODB_WORK')
    create_connection_files(config, 'OEREB_WORK')    

    return config