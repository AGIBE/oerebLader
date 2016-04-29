# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import cx_Oracle
import datetime
import codecs
import arcpy

logger = logging.getLogger('oerebLaderLogger')

def get_layers(config):
    ebenen = []
    gpr_code = config['LIEFEREINHEIT']['gprcode']
    gpr_sql = "SELECT EBECODE FROM GPR WHERE GPRCODE='" + gpr_code + "'"
    ebenen_results = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], gpr_sql)
    for ebene in ebenen_results:
        ebecode = "GEODB." + gpr_code + "_" + ebene[0]
        ebenen.append(ebecode)
    return ebenen

def get_layer_symbfields(config, mxd_layername):
    symbfields = []
    info_sql = "select distinct sym.objekt_ident, sym.objekt, sym.objekt_full, mxd.ebene as layer, symb_attr_orig symb_typ from gdbp.info_symb sym left join gdbp.info_mxd mxd on sym.OBJEKT_IDENT=mxd.OBJEKT_IDENT where mxd.ebene = '" + mxd_layername + "' and mxd.mxd like '%a42pub_oereb_wms_d_fk%'"
    info_results = oerebLader.helpers.sql_helper.readSQL(config['GDBV_WORK']['connection_string'], info_sql)
    for info_result in info_results:
        symbfields_raw = info_result[4]
        if symbfields_raw is not None:
            for symbfields_split in symbfields_raw.split("/"):
                symbfields.append(symbfields_split)
        else:
            symbfields.append(None)
    
    return symbfields

def has_attribute(table, attrname, config):
    result = False
    attr_sql = "SELECT * FROM " + table
    with cx_Oracle.connect(config['GEO_VEK1']['connection_string']) as conn:
        cur = conn.cursor()
        cur.execute(attr_sql)
        descs = cur.description
        for desc in descs:
            if desc[0].upper() == attrname.upper():
                result = True
    return result

class Table:
    def __init__(self, tableName, fieldName, bfsnr, config):
        self.bfsnr = bfsnr
        self.oldConnParams = config['GEO_VEK1']['connection_string']
        self.newConnParams = config['GEODB_WORK']['connection_string']
        self.tableName = tableName
        self.fieldName = fieldName
        self.oldValues = self.__getOldValues()
        self.newValues = self.__getNewValues()
        self.addedValues = list(set(self.newValues)-set(self.oldValues))
        self.removedValues = list(set(self.oldValues)-set(self.newValues))
        self.hasChangedValues = self.__getDifferenceStatus()
    
    def __getOldValues(self):
        return self.__getValues(self.oldConnParams)
    
    def __getNewValues(self):
        return self.__getValues(self.newConnParams)
        
    def __getValues(self, connString):
        sql = "SELECT DISTINCT " + self.fieldName + " FROM " + self.tableName + " WHERE BFSNR=" + str(self.bfsnr)
        rows = oerebLader.helpers.sql_helper.readSQL(connString, sql)
        values = []
        for row in rows:
            if row[0] is not None:
                values.append(unicode(row[0]))
        return values
        
    def __getDifferenceStatus(self):
        if len(self.addedValues) > 0 or len(self.removedValues) > 0:
            return True
        else:
            return False

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    bfsnr = config['LIEFEREINHEIT']['bfsnr']
    
    log_directory = config['LOGGING']['log_directory']
    outputFile = os.path.join(log_directory, "s43_legendenrelevanteAttribute.log")
    logger.info("Ausgabe erfolgt in " + outputFile)

    if os.path.exists(outputFile):
        archive_logfilename = os.path.join(log_directory, "s43_legendenrelevanteAttribute_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".log")
        archive_logfile = os.path.join(log_directory, archive_logfilename)
        os.rename(outputFile, archive_logfile)
    
    layers = []
    for layer in get_layers(config):
        # Tabellen werden nicht symbolisiert, daher müssen sie auch nicht untersucht werden.
        featureclass = os.path.join(config['GEODB_WORK']['connection_file'], layer)
        if arcpy.Describe(featureclass).datasetType != "Table":
            # Die FeatureClass NPL_GNGU enthält nie Objekte, die in der ÖREB-Karte symbolisiert werden.
            # Sie kann deshalb ignoriert werden:
            if not layer.endswith("GNGU"):
                mxd_layername = layer + "_" + unicode(bfsnr)
                symbFields = get_layer_symbfields(config, mxd_layername)
                # Hat die FeatureClass ein BESCHRIEB-Feld oder ein ZONENNAME-Feld (enthält die gemeindespezifische Bezeichnung),
                # wird dieses immer auch untersucht.
                if has_attribute(layer, "BESCHRIEB", config):
                    symbFields.append("BESCHRIEB")
                if has_attribute(layer, "ZONENNAME", config):
                    symbFields.append("ZONENNAME")
                layerDict = {
                    "name": layer,
                    "mxdname": mxd_layername,
                    "symbFields": symbFields
                }
                layers.append(layerDict)

    result_file = codecs.open(outputFile, "w","utf-8")
    outStr = ""

    for layer in layers:
        symbFields = layer['symbFields']
        
        # symbFields ist leer (keine Items in der Liste) => der Layer ist im MXD gar nicht symbolisiert.
        # Für diesen Layer muss via das Feld OBJECTID geprüft werden, ob er neu nicht doch Werte aufweist.
        if len(symbFields) == 0:
            outStr += layer["mxdname"] + ": der Layer wurde im MXD nicht gefunden. Es wird nach OBJECTID gesucht.\n"
            symbFields = ['OBJECTID']

        # symbFields ist None => der Layer wird nicht mit einem Symbol-Feld dargestellt. Die Symbolisierung muss sowieso nicht angepasst werden.
        if symbFields[0] is None:
            outStr += layer["mxdname"] + ": wird nicht geprüft, der Layer wird auf kein bestimmtes Feld symbolisiert.\n"
        else:
            for symbField in symbFields:
                t = Table(layer["name"], symbField, bfsnr, config)
                if t.hasChangedValues == True:
                    outStr += t.tableName + " (" + t.fieldName + u"): es hat Änderungen\n"
                    outStr += "    Neue Werte: " + "/".join(t.addedValues) + "\n"
                    outStr += "    Verschwundene Werte: " + "/".join(t.removedValues) + "\n"
                else:
                    outStr += t.tableName + " (" + t.fieldName + u"): keine Änderungen\n"
        
        outStr += "===================================================================================================================\n"
            
    result_file.write(outStr)