# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import oerebLader.logging
import codecs
import sys
import yaml
import urllib2
import jinja2
import os

def run_update_woinfo(target, create_tables):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("update_woinfo", config)
    if target == 'work':
        pg_connection = config['OEREB_WORK_PG']['connection']
    elif target == 'vek2':
        pg_connection = config['OEREB_VEK2_PG']['connection']
    elif target == 'vek1':
        pg_connection = config['OEREB_VEK1_PG']['connection']
    else:
        logger.error("Kein gültiger Instanzname angegeben")
        sys.exit()

    logger.info("Datenbank %s ausgewählt" % (target))

    if create_tables:
        logger.info("Erstelle WebOffice-Infotabellen neu...")
        sql_create_statements = config['WEBOFFICE_INFOTABLES']['sql_create_statements']

        with codecs.open(sql_create_statements, "r", "utf-8") as create_sql_file:
            sql = create_sql_file.read()

        pg_connection.db_write(sql)
        logger.info("WebOffice-Infotabellen wurden neu erstellt.")
    else:
        logger.info("WebOffice-Infotabellen werden nicht neu erstellt.")
        logger.info("Bestehende Tabellen werden geleert und abgefüllt.")

    # Aktuelles Config-File des ÖREB-Servers einlesen
    # Dieses enthält Geometrietyp und Themennamen
    oereb_server_configfile = config['WEBOFFICE_INFOTABLES']['oereb_server_config']
    yaml_file = urllib2.urlopen(oereb_server_configfile)
    oereb_server_config = yaml.safe_load(yaml_file)

    wo_tables_to_truncate = ['oereb.wo_flaeche', 'oereb.wo_linie', 'oereb.wo_punkt', 'oereb.wo_revo']

    logger.info("Leere die WebOffice-Infotabellen.")
    for table in wo_tables_to_truncate:
        logger.info(table)
        pg_connection.db_write("truncate table %s" % (table))
    logger.info("WebOffice-Infotabellen geleert.")

    for topic in oereb_server_config['pyramid_oereb']['plrs']:
        schema_name = topic['source']['params']['models'].split('.')[2]
        logger.info("Bearbeite %s" % (schema_name))
        geometry_type = topic['geometry_type']
        if geometry_type == "POINT":
            table_names = ['oereb.wo_punkt']
            geometry_expressions = ["g.geom"]
            where_clauses = [""]
        elif geometry_type == "LINESTRING":
            table_names = ['oereb.wo_linie']
            geometry_expressions = ["st_multi(g.geom)"]
            where_clauses = [""]
        elif geometry_type == "MULTILINESTRING":
            table_names = ['oereb.wo_linie']
            geometry_expressions = ["g.geom"]
            where_clauses = [""]
        elif geometry_type == "POLYGON":
            table_names = ['oereb.wo_flaeche']
            geometry_expressions = ["st_multi(g.geom)"]
            where_clauses = [""]
        elif geometry_type == "MULTIPOLYGON":
            table_names = ['oereb.wo_flaeche']
            geometry_expressions = ["g.geom"]
            where_clauses = [""]
        elif geometry_type == "GEOMETRYCOLLECTION":
            table_names = ['oereb.wo_flaeche', 'oereb.wo_linie', 'oereb.wo_punkt']
            geometry_expressions = ['st_collectionextract(g.geom, 3)','st_collectionextract(g.geom, 2)','(st_dump(st_collectionextract(g.geom, 1))).geom']
            where_clauses = ['where st_isempty(st_collectionextract(g.geom, 3)) = false', 'where st_isempty(st_collectionextract(g.geom, 2)) = false', 'where st_isempty(st_collectionextract(g.geom, 1)) = false']
        else:
            logger.error("Geometrietyp %s ist ungültig" % (geometry_type))
            sys.exit()

        # In der Themenbezeichnung kann es einfache Anführungszeichen haben.
        # Diese müssen escaped werden.
        topic_text_de = (topic['text']['de'].replace("'", "''"))
        topic_text_fr = (topic['text']['fr'].replace("'", "''"))

        if topic.has_key('sub_themes'):
            topic_de = "concat('%s - ', p.sub_theme->>'de')" % (topic_text_de)
            topic_fr = "concat('%s - ', p.sub_theme->>'fr')" % (topic_text_fr)
        else:
            topic_de = "'%s'" % topic_text_de
            topic_fr = "'%s'" % topic_text_fr


        for table_name, geometry_expression, where_clause in zip(table_names, geometry_expressions, where_clauses):
            logger.info("Erstelle SQL-Statements für %s" % (table_name))
            template_vars = {
                'table_name': table_name,
                'geometry_expression': geometry_expression,
                'where_clause': where_clause,
                'schema_name': schema_name,
                'topic_de_expression': topic_de,
                'topic_fr_expression': topic_fr            }
            template_file = config['WEBOFFICE_INFOTABLES']['sql_geom_insert_template']
            templateLoader = jinja2.FileSystemLoader(searchpath=os.path.abspath(os.path.dirname(template_file)))
            templateEnv = jinja2.Environment( loader=templateLoader )
            template = templateEnv.get_template(os.path.basename(template_file))

            insert_statements = template.render(template_vars)
            logger.info(insert_statements)

            logger.info("Führe SQL-Statements aus.")
            pg_connection.db_write(insert_statements)
            logger.info("SQL-Statements ausgeführt.")

        logger.info("Erstelle SQL-Statements für oereb.wo_revo")
        template_vars = {
            'table_name': 'oereb.wo_revo',
            'schema_name': schema_name
        }
        template_file = config['WEBOFFICE_INFOTABLES']['sql_revo_insert_template']
        templateLoader = jinja2.FileSystemLoader(searchpath=os.path.abspath(os.path.dirname(template_file)))
        templateEnv = jinja2.Environment( loader=templateLoader )
        template = templateEnv.get_template(os.path.basename(template_file))

        insert_statements = template.render(template_vars)
        logger.info(insert_statements)

        logger.info("Führe SQL-Statements aus.")
        pg_connection.db_write(insert_statements)
        logger.info("SQL-Statements ausgeführt.")
        
        logger.info("%s beendet." % (schema_name))

    logger.info("Analysiere die WebOffice-Infotabellen.")
    for table in wo_tables_to_truncate:
        logger.info(table)
        pg_connection.db_write("vacuum analyze %s" % (table))
    logger.info("WebOffice-Infotabellen analysiert.")
