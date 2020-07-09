# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.configuration
import AGILib.connection
import os

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

def create_connection(config, key):
    if key.endswith("_PG"):
        connection = AGILib.connection.Connection(db_type="postgres", db=config[key]['database'], username=config[key]['username'], password=config[key]['password'], host=config[key]['host'], port=config[key]['port'])
    else:
        connection = AGILib.connection.Connection(db_type="oracle", db=config[key]['database'], username=config[key]['username'], password=config[key]['password'])
    
    config[key]['connection'] = connection


def get_config():
    config = AGILib.configuration.Configuration(configfile_path=get_general_configfile_from_envvar()).config

    # Connection-Objekte erstellen
    create_connection(config, 'GEODB_WORK')
    create_connection(config, 'OEREB2_WORK')
    create_connection(config, 'OEREB2_TEAM')
    create_connection(config, 'NORM_TEAM')
    create_connection(config, "GEODB_DD_TEAM")
    create_connection(config, "OEREB2APP")
    create_connection(config, "OEREBCUGAPP")
    create_connection(config, "GEO_VEK1")
    create_connection(config, "OEREB2_VEK1")
    create_connection(config, "OEREB2_VEK2")
    create_connection(config, "TBA_WORK")
    create_connection(config, "GDBV_WORK")
    create_connection(config, "GEODB_WORK_PG")
    create_connection(config, "OEREB_WORK_PG")
    create_connection(config, "OEREB_TEAM_PG")
    create_connection(config, "OEREB_VEK2_PG")
    create_connection(config, "OEREB_VEK1_PG")

    # Dictionary mit kommunalen Layern erstellen
    layers = []
    for k, v in config['KOMMUNALE_LAYER'].items():
        layers.append(v)
    config['KOMMUNALE_LAYER'] = layers

    return config