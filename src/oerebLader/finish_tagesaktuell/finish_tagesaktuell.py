# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import oerebLader.logging

def run_finish_tagesaktuell(task_id_geodb):
    task_id_geodb = unicode(task_id_geodb)
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("finish_tagesaktuell", config)
    logger.info("Task-ID GeoDB: %s" % (task_id_geodb))
    finish_sql = "UPDATE ticket SET status=5 WHERE art=5 AND status=4 AND task_id_geodb=%s" % (task_id_geodb)
    config['OEREB_WORK_PG']['connection'].db_write(finish_sql)

    logger.info("Tagesaktueller Import wurde abgeschlossen.")
