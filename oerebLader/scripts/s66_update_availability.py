# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import oerebLader.helpers.sql_helper

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    liefereinheit = unicode(config['LIEFEREINHEIT']['id'])
    bfsnr = unicode(config['LIEFEREINHEIT']['bfsnr'])

    for schema in config['LIEFEREINHEIT']['schemas']:
        logger.info("Aktualisiere " + schema + ".availability")
        update_availability_sql = "INSERT INTO %s.availability (fosnr, available, liefereinheit) VALUES (%s, true, %s)" % (schema, bfsnr, liefereinheit)
        logger.info(update_availability_sql)
        oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], update_availability_sql)

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")