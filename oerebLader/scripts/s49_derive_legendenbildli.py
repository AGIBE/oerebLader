# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import requests
import codecs
import mappyfile
import json
import base64

logger = logging.getLogger('oerebLaderLogger')

def getDARSTC(eib_oid, table, config):
    darst_sql = "SELECT distinct darst_c FROM " + table + " WHERE RVS_ID='" + eib_oid + "'"
    results = oerebLader.helpers.sql_helper.readSQL(config['GEODB_WORK']['connection_string'], darst_sql)

    darst_c = ""
    if len(results) != 1:
        darst_c = "LEEEER!!!"
    else:
        darst_c = results[0][0]
        
    return darst_c

def getEIB(liefereinheit, config, nupla_layers):
    eib_sql = "SELECT EIB_OID, DAR_OID FROM EIGENTUMSBESCHRAENKUNG WHERE EIB_LIEFEREINHEIT=" + unicode(liefereinheit)
    eibs = []
    result_eibs = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], eib_sql)
    
    for r in result_eibs:
        eib_oid = r[0]
        dar_oid = r[1]
        dar_oid = dar_oid.split(".")[-1]
        result = (item for item in nupla_layers if item["id"] == dar_oid).next()
        layer = result["layer"]
        table = result["table"]
        darst_c = getDARSTC(eib_oid, table, config)
        eib = {"eib_oid": eib_oid, "layer": layer, "table": table, "darst_c": darst_c}
        eibs.append(eib)
        
    return eibs

def get_EIB_index(mapfile, eib, bfsnr):
    layer = (item for item in mapfile["layers"] if item["name"].strip('"')==eib["layer"]).next()
    eib_index = "-999"
    # Suche nach BFSNR und DARST_C (d.h. kommunales Symbol)
    for i,cls in enumerate(layer["classes"]):
        # Die Klasse "alle anderen Werte" hat keine Expression.
        # Daher muss sie ignoriert werden.
        if "expression" in cls.keys():
            expression = cls["expression"].strip('"')
            if bfsnr in expression and eib["darst_c"] in expression:
                eib_index = i
    
    # Wenn nicht als kommunales Symbol gefunden
    # wird nun auch in den kantonalen gesucht
    if eib_index == "-999":
        for i,cls in enumerate(layer["classes"]):
            # Die Klasse "alle anderen Werte" hat keine Expression.
            # Daher muss sie ignoriert werden.
            if "expression" in cls.keys():
                expression = cls["expression"].strip('"')
                # der DARST_C muss der Expression genau entsprechen
                # Nur dann ist es ein kantonales Symbol
                if eib["darst_c"]==expression:
                    eib_index=i
                    
    # Wenn auch kein kantonales Symbol gefunden wird,
    # wird das Symbol "alle anderen Werte" genommen.
    # Dieses ist immer das letzte/unterste im Mapfile
    if eib_index == "-999":
        eib_index = len(layer['classes']) - 1
                    
    return eib_index

def get_id_mapping_json(json_filepath):

    with codecs.open(json_filepath, "r", "utf-8") as ff:
        js = json.load(ff)

    return js

def get_mapping_infos(json_object, eib_oid):

    plr_id = ""
    schema = ""

    for id in json_object:
        if id['eib_oid'] == eib_oid:
            plr_id = id['plr_id']
            schema = id['schema']

    return(plr_id, schema)

def download_and_encode_image(image_url):
    encoded_image = 'not found'
    r = requests.get(image_url)
    if r.status_code == 200:
        encoded_image = base64.b64encode(r.content)
    else:
        logger.warning("Legendenbild konnte nicht heruntergeladen werden.")
        logger.warning("HTTP-Status: " + unicode(r.status_code))

    return encoded_image

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")

    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    id_mapping_jsonfile = os.path.join(config['TEMPDIR'], 'id_mapping.json')
    id_mapping_json = get_id_mapping_json(id_mapping_jsonfile)
    legend_basedir = os.path.join(config['GENERAL']['files_be_ch_baseunc'], unicode(config['LIEFEREINHEIT']['id']), unicode(config['ticketnr']), "legenden")

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
    eibs = getEIB(config['LIEFEREINHEIT']['id'], config, nupla_layers,)

    mapfile_path = os.path.join(config['LEGENDS']['legend_mapfile'], "oerebpruef/oerebpruef_de.map")
    logger.info("Mapfile einlesen: " + mapfile_path)
    with codecs.open(mapfile_path, "r", "utf-8") as mapfile:
        mf = mappyfile.loads(mapfile.read())

    logger.info("Der Class-Index für jede EIB wird aus dem Mapfile ausgelesen.")
    already_downloaded_files = []
    for eib in eibs:
        # Index holen
        eib_index = get_EIB_index(mf, eib, unicode(bfsnr))
        
        # URLs und Pfade bilden
        legendicon_url = config['LEGENDS']['legend_mapservice_base_url'] + eib["layer"] + "," + unicode(eib_index)
        filename = eib["layer"].split(".")[1] + "_" + eib["darst_c"] + "_" + unicode(eib_index) + ".png"
        legendicon_file = os.path.join(legend_basedir, filename)
        legendicon_url_files = legend_baseurl + filename
        
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

        # Update TRANSFERSTRUKTUR ORACLE
        eib_sql = "UPDATE EIGENTUMSBESCHRAENKUNG SET EIB_LEGENDESYMBOL_DE='" + legendicon_url_files + "', EIB_LEGENDESYMBOL_FR='" + legendicon_url_files + "' WHERE EIB_OID='" + eib["eib_oid"] + "'"
        oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], eib_sql)

        # Update TRANSFERSTRUKTUR pyramid_oereb
        (plr_id, schema) = get_mapping_infos(id_mapping_json, eib["eib_oid"])
        image = download_and_encode_image(legendicon_url_files)
        legend_entry_sql = "UPDATE " + schema + ".legend_entry SET symbol_url='" + legendicon_url_files + "', symbol='" + image + "' WHERE id='" + plr_id + "'"
        oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], legend_entry_sql)
        
    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")
    
