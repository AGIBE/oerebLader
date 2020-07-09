# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import tempfile
import os
import arcpy

def create_connection_files(config, key, logger):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    temp_directory = tempfile.mkdtemp()
    sde_filename = key + ".sde"
    connection_file = os.path.join(temp_directory, sde_filename)
    logger.info("Erzeuge Connectionfile " + connection_file)
    logger.info("Verwende Datenbank " + database)
    arcpy.CreateDatabaseConnection_management(temp_directory, sde_filename, "ORACLE", database, "DATABASE_AUTH", username, password )
    return connection_file

def delete_connection_files(connection_file, logger):
    logger.info("Lösche Connectionfile " + connection_file)
    if os.path.exists(connection_file):
        os.remove(connection_file)