# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.config
import oerebLader.logging
import os
import datetime

def run_refresh_statistics():
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("refresh_statistics", config)

    logger.info("Statistiken des ÖREB2-Schemas in VEK2 werden aktualisiert.")
    config['OEREB2_VEK2']['connection'].db_callproc('dbms_stats.gather_schema_stats', [config['OEREB2_VEK2']['username']])

    logger.info("Statistiken des ÖREB2-Schemas in VEK1 werden aktualisiert.")
    config['OEREB2_VEK1']['connection'].db_callproc('dbms_stats.gather_schema_stats', [config['OEREB2_VEK1']['username']])

    logger.info(
        "Statistiken der PostGIS-Transferstruktur in VEK2 werden aktualisiert."
    )
    config['OEREB_VEK2_PG']['connection'].db_write("VACUUM ANALYZE")

    logger.info(
        "Statistiken der PostGIS-Transferstruktur in VEK1 werden aktualisiert."
    )
    config['OEREB_VEK1_PG']['connection'].db_write("VACUUM ANALYZE")

    logger.info("Statistiken wurden aktualisiert.")