# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib
import oerebLader.config
import oerebLader.logging
import os
import datetime
import logging
import arcpy
import sys
import tempfile
import git
import shutil
import platform
import psycopg2
import tempfile

def clone_master_repo(master_repo_dir):
    tmpdir = tempfile.mkdtemp()
    cloned_repo = git.Repo.clone_from(master_repo_dir, tmpdir)
    return cloned_repo.working_dir

def get_release_mapfiles(config, logger, valid_art):
    folders = []
    files = []
    geoproducts_sql = "select string_agg(ticket.ID::text, ',' ORDER BY ticket.ID) as ID, string_agg(liefereinheit.BFSNR::text, ',' ORDER BY liefereinheit.BFSNR) as BFSNR, workflow_gpr.gprcode from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.id left join workflow_gpr on liefereinheit.workflow=workflow_gpr.workflow where ticket.STATUS=3 and ticket.ART" + valid_art + " group by gprcode"
    geoproducts = config['OEREB_WORK_PG']['connection'].db_read(geoproducts_sql)
    
    for gpr in geoproducts:
        gprcode = gpr[2].lower()
        if gprcode == 'nupla':
            for layer in config['KOMMUNALE_LAYER']:
                mapfile_name = 'nupla/' + layer['layer'].split(".")[1].replace("nupla_","") + ".map"
                files.append(mapfile_name)
            bfsnr = gpr[1].split(',')
            for bfs in bfsnr:
                bfs_folder = 'nupla/' + bfs + "/"
                folders.append(bfs_folder)
        else:
            folders.append(gprcode)
            
    # Diese drei Verzeichnisse werden immer kopiert!
    folders.append('fonts')
    folders.append('templates')
    folders.append('symbole')
    folders.append('images')
    
    # Allfällige Duplikate entfernen
    files = list(set(files))
    folders = list(set(folders))
    
    return (folders, files)
    
def release_mapfiles(config, logger, valid_art):
    logger.info("Repository oereb wird geklont...")
    oereb_repo_dir = clone_master_repo(config['REPOS']['oereb'])
    logger.info(oereb_repo_dir)
    logger.info("Repository oerebpruef wird geklont...")
    oerebpruef_repo_dir = clone_master_repo(config['REPOS']['oerebpruef'])
    logger.info(oerebpruef_repo_dir)
    
    # Zu kopierende Ordner bzw. Files bestimmen
    released_mapfiles = get_release_mapfiles(config, logger, valid_art)
    mapfile_folders = released_mapfiles[0]
    mapfiles = released_mapfiles[1] 
    
    logger.info("Folgende Mapfile-Ordner werden kopiert:")
    for mff in mapfile_folders:
        mff_src = os.path.join(oerebpruef_repo_dir, "oerebpruef", mff)
        mff_target = os.path.join(oereb_repo_dir, "oereb", mff)
        logger.info("Der Ziel-Ordner wird gelöscht: " + mff_target)
        if os.path.exists(mff_target):
            shutil.rmtree(mff_target)
        logger.info("Der Quell-Ordner wird kopiert: " + mff_src)
        logger.info("nach: " +mff_target)
        # Die Logfiles aus der Migration sollen nicht kopiert werden.
        shutil.copytree(mff_src, mff_target, ignore=shutil.ignore_patterns('*.log'))
        
    logger.info("Folgende Einzel-Mapfiles werden kopiert:")
    for mf in mapfiles:
        mf_src = os.path.join(oerebpruef_repo_dir, "oerebpruef", mf)
        mf_target = os.path.join(oereb_repo_dir, "oereb", mf)
        logger.info("Kopiere..." + mf_src)
        logger.info("...nach " + mf_target)
        shutil.copyfile(mf_src, mf_target)
        
    repo = git.Repo(oereb_repo_dir)
    # Nur wenn das Repo dirty ist, wird überhaupt
    # ein Commit gemacht.
    if repo.is_dirty(untracked_files=True):
        logger.info("git add...")
        repo.git.add(all=True)
        commit_msg = "Release " + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " (" + platform.node()  + ")"
        logger.info("git commit -m " + commit_msg)
        repo.git.commit(m=commit_msg)
        logger.info("git push origin master")
        repo.git.push("origin", "master")
        logger.info("Zentrales ÖREB-Repository wurde aktualisiert.")
        logger.info(config['REPOS']['oereb'])
    else:
        logger.warn("Das Repository hat keine Änderungen detektiert.")
        logger.warn("Es wird nichts committed.")
        
def update_transferdate(config, logger, liefereinheiten, dailyMode):

    logger.info("Ermittle Themen, deren Transferdatum aktualisiert werden muss.")    
    themes_sql = "select distinct the_id from subthema where sth_id in (select distinct sth_id from eigentumsbeschraenkung where eib_liefereinheit in " + liefereinheiten + ") ORDER BY the_id"
    themes_result = config['OEREB2_WORK']['connection'].db_read(themes_sql)
    
    transfer_date = datetime.date.today().isoformat()
    
    for tr in themes_result:
        logger.info("Update Thema " + unicode(tr[0]))
        transfer_date_sql = "update thema set the_transferdate=TO_DATE('" + transfer_date + "', 'YYYY-MM-DD') where the_id=" + unicode(tr[0])
        logger.info(transfer_date_sql)
        logger.info("VEK2 wird aktualisiert.")
        config['OEREB2_VEK2']['connection'].db_write(transfer_date_sql)
        
        # Tagesaktuelles Release - VEK1 wird ebenfalls aktualisiert.
        if dailyMode:
            logger.info("VEK1 wird aktualisiert.")
            config['OEREB2_VEK1']['connection'].db_write(transfer_date_sql)

def get_schema_from_liefereinheit(liefereinheit, connection):
    schemas = []
    liefereinheit = unicode(liefereinheit)
    schema_sql = "select schema from workflow_schema where WORKFLOW in (select workflow from liefereinheit where id='%s')" % (liefereinheit)
    schema_sql_results = connection.db_read(schema_sql)
    for schema_result in schema_sql_results:
        schemas.append(schema_result[0])

    return schemas

def get_pg_tables(connection):
    pg_tables = []
    table_sql = "select ebecode, filter_field from gpr where gprcode='OEREB_PG' order by EBEORDER"
    table_sql_results = connection.db_read(table_sql)
    for table_sql_result in table_sql_results:
        pg_table = (table_sql_result[0], table_sql_result[1])
        pg_tables.append(pg_table)
    
    return pg_tables

def append_transferstruktur(source_connection, target_connection, source_sql, full_tablename):
    # https://codereview.stackexchange.com/questions/115863/run-query-and-insert-the-result-to-another-table
    # Inhalte aus WORK mit COPY TO in ein Temp-File schreiben
    copy_to_query = "COPY (%s) TO STDOUT WITH (FORMAT text)" % (source_sql)
    with tempfile.NamedTemporaryFile('w+t') as fp:
        with psycopg2.connect(source_connection.postgres_connection_string) as source_connection:
            with source_connection.cursor() as source_cursor:
                source_cursor.copy_expert(copy_to_query, fp)

        # Alles ins File rausschreiben
        fp.flush()
        # File auf Anfang zurücksetzen
        fp.seek(0)

        with psycopg2.connect(target_connection.postgres_connection_string) as target_connection:
            target_connection.autocommit = True
            with target_connection.cursor() as target_cursor:
                target_cursor.copy_from(file=fp, table=full_tablename)


def run_release(dailyMode):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("release", config)
    logger.info("Der Release wird initialisiert!")
    
    # Connection-Files erstellen
    config['GEODB_WORK']['connection_file'] = config['GEODB_WORK']['connection'].create_sde_connection()
    config['OEREB2_WORK']['connection_file'] = config['OEREB2_WORK']['connection'].create_sde_connection()
    config['NORM_TEAM']['connection_file'] = config['NORM_TEAM']['connection'].create_sde_connection()
    config['OEREB2_TEAM']['connection_file'] = config['OEREB2_TEAM']['connection'].create_sde_connection()
    
    logger.info("Folgende Tickets werden released:")
    if dailyMode:
        valid_art = "=5"
    else:
        valid_art = "!=5"
    
    ticket_sql = "select ticket.ID, liefereinheit.ID, liefereinheit.NAME, liefereinheit.BFSNR, liefereinheit.WORKFLOW, ticket.art from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.id where ticket.STATUS=3 and ticket.ART" + valid_art
    tickets = config['OEREB_WORK_PG']['connection'].db_read(ticket_sql)
    liefereinheiten = []
    
    #Geoprodukt kopieren
    logger.info("Das Geoprodukt wird freigegeben.")
    for ticket in tickets:
        logger.info("ID: " + unicode(ticket[0]) + "/ Liefereinheit: " + unicode(ticket[1]) + "/ Workflow: " + unicode(ticket[4]))
        workflow = unicode(ticket[4])
        liefereinheiten.append(unicode(ticket[1]))

        gpr_sql = "SELECT gprcode FROM workflow_gpr WHERE workflow='" + workflow + "'"
        gpr_result = config['OEREB_WORK_PG']['connection'].db_read(gpr_sql)
        gpr_codes = []
        if len(gpr_result) > 0:
            for gpr in gpr_result:
                gpr_codes.append(gpr[0])
        gpr_where_clause = "GPRCODE IN ('" + "','".join(gpr_codes) + "')"
        logger.info("GPR WHERE Clause: " + gpr_where_clause)
        gpr_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE, GPRCODE FROM GPR WHERE " + gpr_where_clause
        ebenen = config['OEREB_WORK_PG']['connection'].db_read(gpr_sql)
        for ebene in ebenen:
            ebene_name = ebene[3] + "_" + ebene[0]
            source = os.path.join(config['GEODB_WORK']['connection_file'], config['GEODB_WORK']['username'] + "." + ebene_name)
            source_layer = ebene_name + "_" + unicode(ticket[3])
            target = os.path.join(config['NORM_TEAM']['connection_file'], config['NORM_TEAM']['username'] + "." + ebene_name)
            target_layer = "target_" + ebene_name + "_" + unicode(ticket[3])
            where_clause = ""
            delete_sql = "DELETE FROM " + ebene_name
            if ebene[1] is not None:
                if ebene[2] == 'BFSNR':
                    where_clause = ebene[1] + "=" + unicode(ticket[3])
                elif ebene[2] == 'LIEFEREINHEIT':
                    where_clause = ebene[1] + "=" + unicode(ticket[1])
                delete_sql = delete_sql + " WHERE " + where_clause
            if arcpy.Describe(source).datasetType=='Table':
                if where_clause == "":
                    arcpy.MakeTableView_management(source, source_layer)
                    arcpy.MakeTableView_management(target, target_layer)
                else:
                    arcpy.MakeTableView_management(source, source_layer, where_clause)
                    arcpy.MakeTableView_management(target, target_layer, where_clause)
            else:
                if where_clause == "":
                    arcpy.MakeFeatureLayer_management(source, source_layer)
                    arcpy.MakeFeatureLayer_management(target, target_layer)
                else:
                    arcpy.MakeFeatureLayer_management(source, source_layer, where_clause)
                    arcpy.MakeFeatureLayer_management(target, target_layer, where_clause)

            logger.info("Deleting...")
            logger.info(delete_sql)
            config['NORM_TEAM']['connection'].db_write(delete_sql)
            logger.info("Appending...")
            arcpy.Append_management(source_layer, target, "TEST")
            logger.info("Counting..")
            source_count = int(arcpy.GetCount_management(source_layer)[0])
            logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
            target_count = int(arcpy.GetCount_management(target_layer)[0])
            logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
            if source_count!=target_count:
                logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                logger.error("Release wird abgebrochen!")
                sys.exit()

    # Transferstruktur PostGIS kopieren wenn es Tickets hat
    if len(tickets) > 0:
        logger.info("Kopiere Transferstruktur PostGIS...")
        pg_tables = get_pg_tables(config['OEREB_WORK_PG']['connection'])
        # https://stackoverflow.com/questions/3940128/how-can-i-reverse-a-list-in-python#3940137
        pg_tables_reversed = pg_tables[::-1]
        # Doppelte Liefereinheiten entfernen
        liefereinheiten = list(set(liefereinheiten))
        for liefereinheit in liefereinheiten:
            logger.info("Kopiere Liefereinheit %s..." % (unicode(liefereinheit)))
            # Schema(s) der Liefereinheit holen
            schemas = get_schema_from_liefereinheit(liefereinheit, config['OEREB_WORK_PG']['connection'])
            for schema in schemas:
                logger.info("Verarbeite Schema %s..." % (schema))
                # Löschen in TEAM
                logger.info("Transferstruktur TEAM leeren...")
                for pg_table in pg_tables:
                    full_tablename = schema + "." + pg_table[0]
                    where_clause = "%s=%s" % (pg_table[1], unicode(liefereinheit))
                    delete_sql = "DELETE FROM %s WHERE %s" % (full_tablename, where_clause) 
                    logger.info(delete_sql)
                    config['OEREB_TEAM_PG']['connection'].db_write(delete_sql)
                # Beim Einfügen muss die umgekehrte Tabellen-Reihenfolge als beim Löschen verwendet werden
                # Grund: Foreign Key-Constraints
                logger.info("Appending...")
                for pg_table in pg_tables_reversed:
                    full_tablename = schema + "." + pg_table[0]
                    where_clause = "%s=%s" % (pg_table[1], unicode(liefereinheit))
                    source_sql = "SELECT * FROM %s WHERE %s" % (full_tablename, where_clause)
                    logger.info(source_sql)
                    append_transferstruktur(config['OEREB_WORK_PG']['connection'], config['OEREB_TEAM_PG']['connection'], source_sql, full_tablename)
                    # QS (Objekte zählen)
                    logger.info("Counting..")
                    source_count = len(config['OEREB_WORK_PG']['connection'].db_read(source_sql))
                    target_count = len(config['OEREB_TEAM_PG']['connection'].db_read(source_sql))
                    logger.info("Anzahl Features im Quell-Layer: " + unicode(source_count))
                    logger.info("Anzahl Features im Ziel-Layer: " + unicode(target_count))
                    if source_count!=target_count:
                        logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                        logger.error("Release wird abgebrochen!")
                        sys.exit()
                
    # Transferstruktur Oracle kopieren wenn es Tickets hat
    if len(tickets) > 0:
        # Doppelte Liefereinheiten entfernen
        liefereinheiten = list(set(liefereinheiten))
        # WHERE-Clause bilden
        liefereinheiten_joined = "(" + ",".join(liefereinheiten) + ")"
        oereb_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='OEREB'"
        oereb_ebenen = config['OEREB_WORK_PG']['connection'].db_read(oereb_sql)
        for oereb_ebene in oereb_ebenen:
            oereb_table = oereb_ebene[0]
            oereb_liefereinheit_field = oereb_ebene[1]
            oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_table, oereb_liefereinheit_field, liefereinheiten_joined)
            logger.info("Deleting Transferstruktur neu...")
            logger.info(oereb_delete_sql)
            config['OEREB2_TEAM']['connection'].db_write(oereb_delete_sql)
            
            # Truncate/Append für Transferstruktur neu
            source2 = os.path.join(config['OEREB2_WORK']['connection_file'], config['OEREB2_WORK']['username'] + "." + oereb_table)
            source2_layer = oereb_table + "2_source_layer"
            target2 = os.path.join(config['OEREB2_TEAM']['connection_file'], config['OEREB2_TEAM']['username'] + "." + oereb_table)
            target2_layer = oereb_table + "2_target_layer"
            where_clause = oereb_liefereinheit_field + " IN " + liefereinheiten_joined
            logger.info("WHERE-Clause: " + where_clause)
            if arcpy.Describe(source2).datasetType=='Table':
                # MakeTableView funktioniert nicht, da mangels OID-Feld keine Selektionen gemacht werden können
                # MakeQueryTable funktioniert, da hier ein virtuelles OID-Feld erstellt wird. Im Gegenzug wird die
                # Tabelle temporär zwischengespeichert.
                arcpy.MakeQueryTable_management(source2, source2_layer, 'ADD_VIRTUAL_KEY_FIELD', '#', '#',  where_clause)
            else:
                arcpy.MakeFeatureLayer_management(source2, source2_layer, where_clause)
                
            logger.info("Appending...")
            arcpy.Append_management(source2_layer, target2, "TEST")
            # Die QueryTables/FeatureLayers müssen nach dem Append gemacht werden,
            # da der QueryTable nicht mehr live auf die Daten zugreift, sondern
            # auf der Festplatte zwischengespeichert ist.
            if arcpy.Describe(source2).datasetType=='Table':
                arcpy.MakeQueryTable_management(target2, target2_layer, 'ADD_VIRTUAL_KEY_FIELD', '#', '#',  where_clause)
            else:
                arcpy.MakeFeatureLayer_management(target2, target2_layer, where_clause)
            logger.info("Counting..")
            source2_count = int(arcpy.GetCount_management(source2_layer)[0])
            logger.info("Anzahl Features im Quell-Layer: " + unicode(source2_count))
            target2_count = int(arcpy.GetCount_management(target2_layer)[0])
            logger.info("Anzahl Features im Ziel-Layer: " + unicode(target2_count))
            if source2_count!=target2_count:
                logger.error("Fehler beim Kopieren. Anzahl Features in der Quelle und im Ziel sind nicht identisch!")
                logger.error("Release wird abgebrochen!")
                sys.exit()

        # Mapfiles kopieren
        logger.info("Mapfiles werden kopiert (oerebpruef->oereb)...")
        release_mapfiles(config, logger, valid_art)
        
        # Nachführungsdatum in Tabelle THEMA schreiben
        logger.info("Nachführungsdaten in der Tabelle THEMA wird aktualisiert.")
        update_transferdate(config, logger, liefereinheiten_joined, dailyMode)
        
        
        # GeoDB-Tabellen schreiben (Flag, Task)
        # sowie GeoDB-Taskid in die TICKET-Tabelle zurückschreiben
        #TODO: Workbench so anpassen, dass auch mehrere Geoprodukte pro Ticket korrekt verarbeitet werden. 
        fme_script = os.path.splitext(__file__)[0] + "_geodb.fmw"
        fme_logfile = os.path.join(config['LOGGING']['log_directory'], os.path.split(fme_script)[1].replace(".fmw","_fme.log"))
        logger.info("Script " +  fme_script + " wird ausgeführt.")
        logger.info("Das FME-Logfile heisst: " + fme_logfile)
        parameters = {
            'WORK_DB': config['OEREB_WORK_PG']['database'],
            'WORK_USERNAME': config['OEREB_WORK_PG']['username'],
            'WORK_PASSWORD': config['OEREB_WORK_PG']['password'],
            'WORK_HOST': config['OEREB_WORK_PG']['host'],
            'WORK_PORT': unicode(config['OEREB_WORK_PG']['port']),
            'TEAM_DB': config['GEODB_DD_TEAM']['database'],
            'TEAM_USERNAME': config['GEODB_DD_TEAM']['username'],
            'TEAM_PASSWORD': config['GEODB_DD_TEAM']['password'],
            'ART_CLAUSE': valid_art
        }

        fmerunner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_logfile, fme_logfile_archive=True)
        fmerunner.run()
        if fmerunner.returncode != 0:
            logger.error("FME-Script %s abgebrochen." % (fme_script))
            raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        
        # OEREBSTA aktualisieren
        logger.info("Geoprodukt OEREBSTA wird aktualisiert.")
        oerebsta_updated = False
        for ticket in tickets:
            # Nur bei TICKETART=1 (Erstimport) wird OEREBSTA aktualisiert.
            if ticket[5] == 1:
                bfsnr = unicode(ticket[3])
                logger.info("Aktualisiere BFSNR " + bfsnr)
                oerebsta_sql = "UPDATE norm.oerebsta_oestatus SET status=1 where bfsnr=" + bfsnr
                oerebsta_updated = True
                try:
                    config['NORM_TEAM']['connection'].db_write(oerebsta_sql)
                except Exception as ex:
                    logger.error("Fehler beim Aktualisieren von OEREBSTA.")
                    logger.error(unicode(ex))
                    logger.error("Script wird abgebrochen!")
                    sys.exit()
        
        # Ticket-Status aktualisieren
        logger.info("Ticket-Stati werden aktualisiert.")
        ilader_tasks = set()
        for ticket in tickets:
            # iLader-Task ermitteln (sofern vorhanden)
            sql_iLader_task = "SELECT task_id_geodb FROM ticket where id=" + unicode(ticket[0])
            taskid = config['OEREB_WORK_PG']['connection'].db_read(sql_iLader_task)[0][0]
            if taskid is not None:
                ilader_tasks.add(unicode(taskid))
            else:
                logger.warn("Für das Ticket Nr. " + unicode(ticket[0]) + " wurde kein iLader-Task angelegt.")
                logger.warn("Dieses Ticket bzw. dessen Geoprodukt muss über die reguläre Triggerfunktion importiert werden.")
                
            logger.info("Ticket-Status des Tickets " + unicode(ticket[0]) + " wird auf 4 gesetzt!")
            sql_update_ticket_status = "UPDATE ticket SET release=CURRENT_TIMESTAMP, status=4 WHERE id=" + unicode(ticket[0])
            try:
                config['OEREB_WORK_PG']['connection'].db_write(sql_update_ticket_status)
            except Exception as ex:
                logger.error("Fehler beim Updaten des Ticket-Status!")
                logger.error(unicode(ex))
                logger.error("Script wird abgebrochen!")
                sys.exit()
        
        logger.warn("Folgende iLader-Tasks müssen nun importiert werden:")
        for iLader_task in ilader_tasks:
            logger.warn("iLader run " + iLader_task)
        
        if oerebsta_updated == True:
            oerebsta_task_sql = "select t.task_objectid from geodb_dd.tb_task t left join geodb_dd.tb_flag_agi f on t.FLAG_OBJECTID=f.FLAG_OBJECTID where f.GPR_BEZEICHNUNG='OEREBSTA' and t.TASK_STATUS=2"
            oerebsta_tasks = config['GEODB_DD_TEAM']['connection'].db_read(oerebsta_task_sql)
            logger.warn("OEREBSTA wurde aktualisiert und muss ebenfalls importiert werden:")
            for ot in oerebsta_tasks:
                logger.warn("iLader run " + unicode(ot[0]))

    # Connection-Files löschen
    config['GEODB_WORK']['connection'].delete_all_sde_connections()
    config['OEREB2_WORK']['connection'].delete_all_sde_connections()
    config['NORM_TEAM']['connection'].delete_all_sde_connections()
    config['OEREB2_TEAM']['connection'].delete_all_sde_connections()
            
    logger.info("Alle Ticket-Stati aktualisiert.")
    logger.info("Release abgeschlossen.")
    