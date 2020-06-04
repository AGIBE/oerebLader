# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import uuid
import oerebLader.helpers.sql_helper

logger = logging.getLogger('oerebLaderLogger')

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    liefereinheit = unicode(config['LIEFEREINHEIT']['id'])
    update_date = datetime.datetime.now()
    office_id = config['LIEFEREINHEIT']['amt_oid']

    for schema in config['LIEFEREINHEIT']['schemas']:
        logger.info("Aktualisiere " + schema + ".data_integration")
        logger.info("Hole Office-ID...")
        id = uuid.uuid4()
        insert_data_integration_sql = "INSERT INTO %s.data_integration (id, date, office_id, liefereinheit) VALUES ('%s', '%s', '%s', %s)" % (schema, id, update_date, office_id, liefereinheit)
        logger.info(insert_data_integration_sql)
        oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], insert_data_integration_sql)

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")