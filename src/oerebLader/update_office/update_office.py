# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.logging
import oerebLader.update_office.excel
import logging
import os
import datetime
import cx_Oracle
import psycopg2
from psycopg2.extras import Json
import sys

def run_update_office(target):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("update_office", config)
    if target == 'work':
        pg_connection = config['OEREB_WORK_PG']['connection']
        ora_connection = config['OEREB2_WORK']['connection']
    elif target == 'team':
        pg_connection = config['OEREB_TEAM_PG']['connection']
        ora_connection = config['OEREB2_TEAM']['connection']
    elif target == 'vek2':
        pg_connection = config['OEREB_VEK2_PG']['connection']
        ora_connection = config['OEREB2_VEK2']['connection']
    elif target == 'vek1':
        pg_connection = config['OEREB_VEK1_PG']['connection']
        ora_connection = config['OEREB2_VEK1']['connection']
    else:
        logger.error("Kein gültiger Instanzname angegeben")
        sys.exit()

    logger.info("Alle Office- und AMT-Tabellen in %s werden aktualisiert." % (target))
    bundesthemen = ",".join(config['GENERAL']['bundesthemen'])
    liefereinheiten_sql = "SELECT liefereinheit.id , string_agg(workflow_schema.SCHEMA, ',' ORDER BY workflow_schema.SCHEMA) schemas FROM liefereinheit LEFT JOIN workflow_schema ON liefereinheit.WORKFLOW = workflow_schema.WORKFLOW where liefereinheit.id not in (%s,9900,9910,9920) GROUP BY liefereinheit.id" % (bundesthemen)
    logger.info(liefereinheiten_sql)
    liefereinheiten_result = config['OEREB_WORK_PG']['connection'].db_read(liefereinheiten_sql)
    for row in liefereinheiten_result:
        liefereinheit = row[0]
        logger.info("Verarbeite Liefereinheit %s..." % (unicode(liefereinheit)))
        ar = oerebLader.update_office.excel.AmtReader(config['GENERAL']['amt_tabelle'], "AMT")
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
            # Alles in ein und derselben Transaktion, daher nicht mit AGILib
            with cx_Oracle.connect(ora_connection.username, ora_connection.password, ora_connection.db) as conn_ora:
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

                with psycopg2.connect(pg_connection.postgres_connection_string) as conn:
                    cur = conn.cursor()
                    cur.execute(office_delete_sql, (liefereinheit,))
                    cur.execute(office_insert_sql, office_sql_insert_values)
                    cur.execute(public_law_restriction_sql, office_sql_update_values)
                    cur.execute(geometry_sql, office_sql_update_values)
                    cur.execute(document_sql, office_sql_update_values)
                    cur.execute(reference_definition_sql, office_sql_update_values)
                    cur.execute(data_integration_sql, office_sql_update_values)
                    conn.commit()
        