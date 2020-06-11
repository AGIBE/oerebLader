# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.log_helper
import oerebLader.helpers.sql_helper
import oerebLader.helpers.excel_helper
import logging
import os
import datetime
import cx_Oracle
import psycopg2
from psycopg2.extras import Json
import sys

def init_logging(config):
    log_directory = os.path.join(
        config['LOGGING']['basedir'], "update_office"
    )
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "update_office.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "update_office" + datetime.datetime.now(
        ).strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)

    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(
        oerebLader.helpers.log_helper.create_loghandler_file(logfile)
    )
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False

    return logger

def run_update_office(target):
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    if target == 'work':
        pg_connectionstring = config['OEREB_WORK_PG']['connection_string']
        ora_connectionstring = config['OEREB2_WORK']['connection_string']
    elif target == 'team':
        pg_connectionstring = config['OEREB_TEAM_PG']['connection_string']
        ora_connectionstring = config['OEREB2_TEAM']['connection_string']
    elif target == 'vek2':
        pg_connectionstring = config['OEREB_VEK2_PG']['connection_string']
        ora_connectionstring = config['OEREB2_VEK2']['connection_string']
    elif target == 'vek1':
        pg_connectionstring = config['OEREB_VEK1_PG']['connection_string']
        ora_connectionstring = config['OEREB2_VEK1']['connection_string']
    else:
        logger.error("Kein gültiger Instanzname angegeben")
        sys.exit()

    logger.info("Alle Office- und AMT-Tabellen in %s werden aktualisiert." % (target))
    bundesthemen = ",".join(config['GENERAL']['bundesthemen'])
    liefereinheiten_sql = "SELECT liefereinheit.id , LISTAGG(to_char(workflow_schema.SCHEMA), ',') WITHIN GROUP (ORDER BY workflow_schema.SCHEMA) schemas FROM liefereinheit LEFT JOIN workflow_schema ON liefereinheit.WORKFLOW = workflow_schema.WORKFLOW where liefereinheit.id not in (%s,9900,9910,9920) GROUP BY liefereinheit.id" % (bundesthemen)
    logger.info(liefereinheiten_sql)
    liefereinheiten_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], liefereinheiten_sql)
    for row in liefereinheiten_result:
        liefereinheit = row[0]
        logger.info("Verarbeite Liefereinheit %s..." % (unicode(liefereinheit)))
        ar = oerebLader.helpers.excel_helper.AmtReader(config['GENERAL']['amt_tabelle'], "AMT")
        amt_oid, amt_oid_base, amt_name_de, amt_name_fr, amt_amtimweb_de, amt_amtimweb_fr = ar.get_oid_by_liefereinheit(liefereinheit)
        if amt_oid is None:
            logger.error("Für die Liefereinheit %s wurde kein Eintrag in der AMT-Tabellegefunden. Sie wird nicht verarbeitet." % (unicode(liefereinheit)))
        else:
            logger.info("Folgende Werte wurden aus der AMT-Tabelle eingelesen:")
            logger.info("%s;%s;%s;%s;%s;%s" % (amt_oid, amt_oid_base, amt_name_de, amt_name_fr, amt_amtimweb_de, amt_amtimweb_fr))

            # Transferstruktur ORACLE
            logger.info("Aktualisiere Transferstruktur Oracle")
            amt_delete_sql = "DELETE FROM AMT WHERE AMT_LIEFEREINHEIT=:liefereinheit"
            amt_insert_sql = "insert into amt (amt_oid, amt_name_de, amt_name_fr, amt_amtimweb_de, amt_amtimweb_fr, amt_liefereinheit) values (:amt_oid, :amt_name_de, :amt_name_fr, :amt_amtimweb_de, :amt_amtimweb_fr, :liefereinheit)"
            amt_sql_insert_values = (amt_oid, amt_name_de, amt_name_fr, amt_amtimweb_de, amt_amtimweb_fr, liefereinheit)
            amt_sql_update_values = (amt_oid, liefereinheit)
            eigentumsbeschraenkung_sql = "UPDATE EIGENTUMSBESCHRAENKUNG set AMT_OID=:amt_oid where eib_liefereinheit=:liefereinheit"
            vorschrift_sql = "UPDATE VORSCHRIFT set AMT_OID=:amt_oid where vor_liefereinheit=:liefereinheit"
            flaeche_sql = "UPDATE FLAECHE set AMT_OID=:amt_oid where fla_liefereinheit=:liefereinheit"
            linie_sql = "UPDATE LINIE set AMT_OID=:amt_oid where lin_liefereinheit=:liefereinheit"
            punkt_sql = "UPDATE PUNKT set AMT_OID=:amt_oid where pun_liefereinheit=:liefereinheit"
            with cx_Oracle.connect(ora_connectionstring) as conn_ora:
                cur_ora = conn_ora.cursor()
                cur_ora.execute(amt_delete_sql, (liefereinheit,))
                cur_ora.execute(amt_insert_sql, amt_sql_insert_values)
                cur_ora.execute(eigentumsbeschraenkung_sql, amt_sql_update_values)
                cur_ora.execute(vorschrift_sql, amt_sql_update_values)
                cur_ora.execute(flaeche_sql, amt_sql_update_values)
                cur_ora.execute(linie_sql, amt_sql_update_values)
                cur_ora.execute(punkt_sql, amt_sql_update_values)
                conn_ora.commit()            

            # Transferstruktur PostgreSQL
            logger.info("Aktualisiere Transferstruktur PostgreSQL")
            for schema in row[1].split(","):
                logger.info("Bearbeite Schema %s" % (schema))
                office_delete_sql = "delete from " + schema + ".office where liefereinheit=%s"
                office_insert_sql = "insert into " + schema + ".office (id, name, office_at_web, liefereinheit) values (%s, %s, %s, %s)"
                office_sql_insert_values = (amt_oid, Json({'de': amt_name_de, 'fr': amt_name_fr}) , amt_amtimweb_de, liefereinheit)
                office_sql_update_values = (amt_oid, liefereinheit)
                public_law_restriction_sql = "update " + schema + ".public_law_restriction set office_id=%s where liefereinheit=%s"
                geometry_sql = "update " + schema + ".geometry set office_id=%s where liefereinheit=%s"
                document_sql = "update " + schema + ".document set office_id=%s where liefereinheit=%s"
                reference_definition_sql = "update " + schema + ".reference_definition set office_id=%s where liefereinheit=%s"
                data_integration_sql = "update " + schema + ".data_integration set office_id=%s where liefereinheit=%s"

                with psycopg2.connect(pg_connectionstring) as conn:
                    cur = conn.cursor()
                    cur.execute(office_delete_sql, (liefereinheit,))
                    cur.execute(office_insert_sql, office_sql_insert_values)
                    cur.execute(public_law_restriction_sql, office_sql_update_values)
                    cur.execute(geometry_sql, office_sql_update_values)
                    cur.execute(document_sql, office_sql_update_values)
                    cur.execute(reference_definition_sql, office_sql_update_values)
                    cur.execute(data_integration_sql, office_sql_update_values)
        