# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.sql_helper
import logging
import os
import cx_Oracle
import datetime
import codecs

logger = logging.getLogger('oerebLaderLogger')

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
    outputFile = os.path.join(log_directory, "s43_legendenrelevanteAttribute_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".log")
    logger.info("Ausgabe erfolgt in " + outputFile)

    # Definition aller Ebenen mit allen legendenrelevanten Feldern
    #TODO: legendenrelevante Felder aus INFO_SYMB_VW auslesen
    layers = [
        {"name": "GEODB.NPL_GNGZ", "symbField": "ZONENABK"},
        {"name": "GEODB.NPL_UEUZ", "symbField": "KANTART"},
        {"name": "GEODB.NPL_UELAERM", "symbField": "KANTART"},
        {"name": "GEODB.NPL_UEUL", "symbField": "KANTART"},
        {"name": "GEODB.NPL_UEWAAB", "symbField": "KANTART"},
        {"name": "GEODB.NPL_VEFE", "symbField": "KANTART"},
        {"name": "GEODB.NPL_NHSF", "symbField": "KANTART"},
        {"name": "GEODB.NPL_NHSL", "symbField": "KANTART"},
        {"name": "GEODB.NPL_NHSP", "symbField": "KANTART"},
        {"name": "GEODB.NPL_WEWRF", "symbField": "ART"},
        {"name": "GEODB.NPL_WEWRL", "symbField": "ART"},
        {"name": "GEODB.NPL_GEFF", "symbField": "STUFE"},
        # {"name": "GEODB.NPL_WAABPER", "symbField": "KANTART"}, wird nicht getestet, da nicht auf ein Feld symbolisiert wird
        {"name": "GEODB.NPL_GEGEWF", "symbField": "ART"},
        {"name": "GEODB.NPL_GEGEWL", "symbField": "ART"},
        {"name": "GEODB.NPL_GNNUTZZO", "symbField": "NZTYP"},
        {"name": "GEODB.NPL_GNNUTZZO", "symbField": "BKTYP"},
        # {"name": "GEODB.NPL_GNBAUW", "symbField": "KANTART"}, wird nicht getestet, da nicht auf ein Feld symbolisiert wird
        {"name": "GEODB.NPL_UEPROJ", "symbField": "BESCHRIEB"}
    ]

    result_file = codecs.open(outputFile, "w","utf-8")

    for layer in layers:
        t = Table(layer["name"], layer["symbField"], bfsnr, config)
        if t.hasChangedValues == True:
            outStr = t.tableName + " (" + t.fieldName + u"): es hat Änderungen\n"
            outStr = outStr + "    Neue Werte: " + "/".join(t.addedValues) + "\n"
            outStr = outStr + "    Verschwundene Werte: " + "/".join(t.removedValues) + "\n"
        else:
            outStr = t.tableName + " (" + t.fieldName + u"): keine Änderungen\n"
        result_file.write(outStr)    