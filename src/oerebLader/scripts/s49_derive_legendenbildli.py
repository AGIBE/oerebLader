# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import requests
import codecs
import mappyfile
import base64
import operator
import itertools
import uuid
import json
import psycopg2
from psycopg2.extras import Json
import time

logger = logging.getLogger('oerebLaderLogger')

def get_darstc(plr_id, table, config):
    darst_sql = "SELECT distinct darst_c FROM " + table + " WHERE RVS_ID='" + plr_id + "'"
    results = oerebLader.helpers.sql_helper.readSQL(config['GEODB_WORK']['connection_string'], darst_sql)

    darst_c = ""
    if len(results) != 1:
        darst_c = "LEEEER!!!"
    else:
        darst_c = results[0][0]
        
    return darst_c

def get_public_law_restriction_per_schema(liefereinheit, config, schema):

    plr_sql = "SELECT id, information, topic, sub_theme, published_from, view_service_id, office_id FROM " + schema + ".public_law_restriction where liefereinheit=" + unicode(liefereinheit)
    return oerebLader.helpers.sql_helper.readPSQL(config['OEREB_WORK_PG']['connection_string'], plr_sql)

def get_public_law_restrictions(liefereinheit, config, nupla_layers, schemas):

    plrs = []

    for schema in schemas:
        result_plrs = get_public_law_restriction_per_schema(liefereinheit, config, schema)
        for r in result_plrs:
            # Felder aus der DB
            view_service_id = r[5]
            # Berechnete Felder
            sub_theme_id = view_service_id.split(".")[-1]
            result = (item for item in nupla_layers if item["id"] == sub_theme_id).next()
            layer = result["layer"]
            table = result["table"]
            plr = {
                "id": r[0],
                "information": r[1],
                "topic": r[2],
                "sub_theme": r[3],
                "published_from": r[4],
                "view_service_id": view_service_id,
                "office_id": r[6],
                "layer": layer,
                "table": table,
                "darstc": get_darstc(r[0], table, config),
                "schema": schema
            }
            plrs.append(plr)
        
    return plrs

def get_public_law_restriction_index(mapfile, plr, bfsnr):
    layer = (item for item in mapfile["layers"] if item["name"].strip('"')==plr["layer"]).next()
    plr_index = "-999"
    # Suche nach BFSNR und DARST_C (d.h. kommunales Symbol)
    for i,cls in enumerate(layer["classes"]):
        # Die Klasse "alle anderen Werte" hat keine Expression.
        # Daher muss sie ignoriert werden.
        if "expression" in cls.keys():
            expression = cls["expression"].strip('"')
            if bfsnr in expression and plr["darstc"] in expression:
                plr_index = i
    
    # Wenn nicht als kommunales Symbol gefunden
    # wird nun auch in den kantonalen gesucht
    if plr_index == "-999":
        for i,cls in enumerate(layer["classes"]):
            # Die Klasse "alle anderen Werte" hat keine Expression.
            # Daher muss sie ignoriert werden.
            if "expression" in cls.keys():
                expression = cls["expression"].strip('"')
                # der DARSTC muss der Expression genau entsprechen
                # Nur dann ist es ein kantonales Symbol
                if plr["darstc"]==expression:
                    plr_index=i
                    
    # Wenn auch kein kantonales Symbol gefunden wird,
    # wird das Symbol "alle anderen Werte" genommen.
    # Dieses ist immer das letzte/unterste im Mapfile
    if plr_index == "-999":
        plr_index = len(layer['classes']) - 1
                    
    return plr_index

def aggregate_plrs(plrs):
    # Inspiriert durch: 
    # https://stackoverflow.com/questions/21674331/group-by-multiple-keys-and-summarize-average-values-of-a-list-of-dictionaries
    grouper = operator.itemgetter('information', 'liefereinheit', 'office_id', 'published_from', 'schema', 'sub_theme', 'symbol_url', 'topic', 'view_service_id')
    result = []
    for key, grp in itertools.groupby(sorted(plrs, key = grouper), grouper):
        temp_dict = dict(zip(['information', 'liefereinheit', 'office_id', 'published_from', 'schema', 'sub_theme', 'symbol_url', 'topic', 'view_service_id'], key))
        ids = []
        for item in grp:
            ids.append(item['id'])
        temp_dict["id"] = ";".join(ids)
        result.append(temp_dict)

    return result

def download_and_encode_image(image_url):
    encoded_image = 'not found'
    r = requests.get(image_url)
    if r.status_code == 200:
        encoded_image = base64.b64encode(r.content)
    else:
        logger.warning("Legendenbild konnte nicht heruntergeladen werden.")
        logger.warning("HTTP-Status: " + unicode(r.status_code))

    # Die Verzögerung wurde nötig, weil es ohne ab und zu
    # zu einem SSLError gekommen ist ("Max retries exceeded with url").
    time.sleep(1)
    return encoded_image

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")

    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")
    schemas = config['LIEFEREINHEIT']['schemas']

    # Das Legendenverzeichnis muss im Voraus vorhanden sein, damit der HTTP-Fetcher
    # im FME dorthin schreiben kann. Er erzeugt keine Directories.
    if not os.path.exists(legend_basedir):
        os.makedirs(legend_basedir)
    if config['GENERAL']['files_be_ch_baseurl'].endswith("/"):
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"
    else:
        legend_baseurl = config['GENERAL']['files_be_ch_baseurl'] + "/" + unicode(config['LIEFEREINHEIT']['id']) + "/" + unicode(config['ticketnr']) + "/legenden/"

    nupla_layers = config["KOMMUNALE_LAYER"]
    
    logger.info("Hole alle EIB_OIDs für die Liefereinheit " + unicode(config['LIEFEREINHEIT']['id']))
    plrs = get_public_law_restrictions(config['LIEFEREINHEIT']['id'], config, nupla_layers, schemas)

    mapfile_path = os.path.join(config['LEGENDS']['legend_mapfile'], "oerebpruef/oerebpruef_de.map")
    logger.info("Mapfile einlesen: " + mapfile_path)
    with codecs.open(mapfile_path, "r", "utf-8") as mapfile:
        mf = mappyfile.loads(mapfile.read())

    logger.info("Der Class-Index für jede PLR wird aus dem Mapfile ausgelesen.")
    already_downloaded_files = []
    for plr in plrs:
        plr['liefereinheit'] = unicode(config['LIEFEREINHEIT']['id'])
        # Index holen
        plr_index = get_public_law_restriction_index(mf, plr, unicode(bfsnr))
        
        # URLs und Pfade bilden
        legendicon_url = config['LEGENDS']['legend_mapservice_base_url'] + plr["layer"] + "," + unicode(plr_index)
        filename = plr["layer"].split(".")[1] + "_" + plr["darstc"] + "_" + unicode(plr_index) + ".png"
        legendicon_file = os.path.join(legend_basedir, filename)
        plr['symbol_url'] = legend_baseurl + filename
        
        # Viele Bilder werden mehrfach referenziert, müssen aber nur
        # einmal heruntergeladen werden.
        if filename not in already_downloaded_files:
            logger.info("Legenden-Bild wird geholt von: " + legendicon_url)
            r = requests.get(legendicon_url)
            if r.status_code == 200:
                with open(legendicon_file, 'wb') as f:
                    f.write(r.content)
                already_downloaded_files.append(filename)
            else:
                logger.warning("Legendenbild konnte nicht heruntergeladen werden.")
                logger.warning("HTTP-Status: " + unicode(r.status_code))

        # Update TRANSFERSTRUKTUR ORACLE (hier muss keine Aggregation erfolgen)
        logger.info("Transferstruktur Oracle wird aktualisiert (Tabelle EIGENTUMSBESCHRAENKUNG)")
        plr_sql = "UPDATE EIGENTUMSBESCHRAENKUNG SET EIB_LEGENDESYMBOL_DE='" + plr['symbol_url'] + "', EIB_LEGENDESYMBOL_FR='" + plr['symbol_url'] + "' WHERE EIB_OID='" + plr["id"] + "'"
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], plr_sql)

    # legend_entry abfüllen (inkl. TypeCode-Aggregation)
    logger.info("Transferstruktur PiostGIS wird aktualisiert.")
    logger.info("Tabellen public_law_restriction und legend_entry.")
    for legend_entry in  aggregate_plrs(plrs):
        legend_entry_id = uuid.uuid4()
        schema = legend_entry['schema']
        symbol_url = legend_entry['symbol_url']
        symbol = download_and_encode_image(symbol_url)
        legend_text = legend_entry['information']
        type_code = uuid.uuid4()
        type_code_list = uuid.uuid4()
        topic = legend_entry['topic']
        sub_theme = legend_entry['sub_theme']
        view_service_id = legend_entry['view_service_id']
        liefereinheit = legend_entry['liefereinheit']
        # sub_theme muss gesondert behandelt werden (#5131)
        if sub_theme is not None:
            legend_entry_insert_sql = "INSERT INTO %s.legend_entry (id, symbol, symbol_url, legend_text, type_code, type_code_list, topic, sub_theme, view_service_id, liefereinheit) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', %s, '%s', %s)" % (schema, legend_entry_id, symbol, symbol_url, Json(legend_text), type_code, type_code_list, topic, Json(sub_theme), view_service_id, liefereinheit)
        else:
            legend_entry_insert_sql = "INSERT INTO %s.legend_entry (id, symbol, symbol_url, legend_text, type_code, type_code_list, topic, view_service_id, liefereinheit) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', %s)" % (schema, legend_entry_id, symbol, symbol_url, Json(legend_text), type_code, type_code_list, topic, view_service_id, liefereinheit)
        oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], legend_entry_insert_sql)
        plr_ids = legend_entry['id'].split(";")
        for plr_id in plr_ids:
            public_law_restriction_update_sql = "UPDATE %s.public_law_restriction SET type_code='%s', type_code_list='%s' WHERE id='%s'" % (schema, type_code, type_code_list, plr_id)
            oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], public_law_restriction_update_sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
