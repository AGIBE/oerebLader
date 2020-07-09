# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime
import uuid
import oerebLader.helpers.sql_helper

logger = logging.getLogger('oerebLaderLogger')

def get_office_id(liefereinheit, schema, config):
    if config['LIEFEREINHEIT']['amt_oid'] is None:
        office_id = "dummy"
        office_sql = "select distinct office_id from %s.public_law_restriction where liefereinheit=%s limit 1" % (schema, liefereinheit)
        office_sql_result = oerebLader.helpers.sql_helper.readPSQL(config['OEREB_WORK_PG']['connection_string'], office_sql)
        if len(office_sql_result) == 1:
            office_id = office_sql_result[0][0]

        return office_id
    else:
        return config['LIEFEREINHEIT']['amt_oid']

def run(config):
    logger.info("Script " +  os.path.basename(__file__) + " wird ausgeführt.")
    liefereinheit = unicode(config['LIEFEREINHEIT']['id'])
    update_date = datetime.datetime.now()

    for schema in config['LIEFEREINHEIT']['schemas']:
        logger.info("Aktualisiere " + schema + ".data_integration")
        id = uuid.uuid4()
        logger.info("Hole Office-ID...")
        office_id = get_office_id(liefereinheit, schema, config)
        insert_data_integration_sql = "INSERT INTO %s.data_integration (id, date, office_id, liefereinheit) VALUES ('%s', '%s', '%s', %s)" % (schema, id, update_date, office_id, liefereinheit)
        logger.info(insert_data_integration_sql)
        oerebLader.helpers.sql_helper.writePSQL(config['OEREB_WORK_PG']['connection_string'], insert_data_integration_sql)

    logger.info("Script " +  os.path.basename(__file__) + " ist beendet.")