# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.log_helper
import oerebLader.helpers.connection_helper
import oerebLader.helpers.sql_helper
import oerebLader.helpers.fme_helper
import os
import datetime
import logging
import arcpy
import fmeobjects
import sys
import tempfile
import git
import shutil
import platform


def init_logging(config):
    log_directory = os.path.join(config['LOGGING']['basedir'], "release")
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, "release.log")
    # Wenn schon ein Logfile existiert, wird es umbenannt
    if os.path.exists(logfile):
        archive_logfile = "release" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfile)
        os.rename(logfile, archive_logfile)
        
    logger = logging.getLogger("oerebLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_file(logfile))
    logger.addHandler(oerebLader.helpers.log_helper.create_loghandler_stream())
    logger.propagate = False
    
    return logger

def clone_master_repo(master_repo_dir):
    tmpdir = tempfile.mkdtemp()
    if "oerebpruef" in master_repo_dir:
        cloned_repo = git.Repo.clone_from(master_repo_dir, tmpdir, branch='layerstruktur')
    else:
        cloned_repo = git.Repo.clone_from(master_repo_dir, tmpdir)
    return cloned_repo.working_dir

def get_release_mapfiles(config, logger):
    folders = []
    geoproducts_sql = "select LISTAGG(ticket.ID, ',') WITHIN GROUP (ORDER BY ticket.ID) as ID, LISTAGG(liefereinheit.BFSNR, ',') WITHIN GROUP (ORDER BY liefereinheit.BFSNR) as BFSNR, workflow_gpr.gprcode from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.id left join workflow_gpr on liefereinheit.workflow=workflow_gpr.workflow where ticket.STATUS=3 and ticket.ART!=5 group by gprcode"
    geoproducts = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], geoproducts_sql)
    
    for gpr in geoproducts:
        gprcode = gpr[2].lower()
        if gprcode == 'nupla':
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
            
    return folders
    
def release_mapfiles(config, logger):
    logger.info("Repository oereb wird geklont...")
    oereb_repo_dir = clone_master_repo(config['REPOS']['oereb'])
    logger.info(oereb_repo_dir)
    logger.info("Repository oerebpruef wird geklont...")
    oerebpruef_repo_dir = clone_master_repo(config['REPOS']['oerebpruef'])
    logger.info(oerebpruef_repo_dir)
    
    # Zu kopierende Ordner bzw. Files bestimmen
    mapfile_folders = get_release_mapfiles(config, logger)
    logger.info("Folgende Mapfile-Ordner werden kopiert:")
    for mff in mapfile_folders:
        mff_src = os.path.join(oerebpruef_repo_dir, "oerebpruef", mff)
        mff_target = os.path.join(oereb_repo_dir, "oereb", mff)
        logger.info("Der Ziel-Ordner wird gelöscht: " + mff_target)
        shutil.rmtree(mff_target)
        logger.info("Der Quell-Ordner wird kopiert: " + mff_src)
        logger.info("nach: " +mff_target)
        # Die Logfiles aus der Migration sollen nicht kopiert werden.
        shutil.copytree(mff_src, mff_target, ignore=shutil.ignore_patterns('*.log'))
        
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

def run_release(dailyMode):
    config = oerebLader.helpers.config.get_config()
    logger = init_logging(config)
    logger.info("Der Release wird initialisiert!")
    
    # Connection-Files erstellen
    config['GEODB_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'GEODB_WORK', logger)
    config['OEREB2_WORK']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'OEREB2_WORK', logger)
    config['NORM_TEAM']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'NORM_TEAM', logger)
    config['OEREB2_TEAM']['connection_file'] = oerebLader.helpers.connection_helper.create_connection_files(config, 'OEREB2_TEAM', logger)
    
    logger.info("Folgende Tickets werden released:")
    if dailyMode:
        valid_art = "=5"
    else:
        valid_art = "!=5"
    
    ticket_sql = "select ticket.ID, liefereinheit.ID, liefereinheit.NAME, liefereinheit.BFSNR, liefereinheit.WORKFLOW from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.id where ticket.STATUS=3 and ticket.ART" + valid_art
    tickets = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], ticket_sql)
    liefereinheiten = []
    
    #Geoprodukt kopieren
    logger.info("Das Geoprodukt wird freigegeben.")
    for ticket in tickets:
        logger.info("ID: " + unicode(ticket[0]) + "/ Liefereinheit: " + unicode(ticket[1]) + "/ Workflow: " + unicode(ticket[4]))
        workflow = unicode(ticket[4])
        liefereinheiten.append(unicode(ticket[1]))

        gpr_sql = "SELECT gprcode FROM workflow_gpr WHERE workflow='" + workflow + "'"
        gpr_result = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], gpr_sql)
        gpr_codes = []
        if len(gpr_result) > 0:
            for gpr in gpr_result:
                gpr_codes.append(gpr[0])
        gpr_where_clause = "GPRCODE IN ('" + "','".join(gpr_codes) + "')"
        logger.info("GPR WHERE Clause: " + gpr_where_clause)
        gpr_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE, GPRCODE FROM GPR WHERE " + gpr_where_clause
        ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], gpr_sql)
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
            oerebLader.helpers.sql_helper.writeSQL(config['NORM_TEAM']['connection_string'], delete_sql)
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
                
    if len(tickets) > 0:
        # Transferstruktur kopieren wenn es Tickets hat
        # Doppelte Liefereinheiten entfernen
        liefereinheiten = list(set(liefereinheiten))
        # WHERE-Clause bilden
        liefereinheiten_joined = "(" + ",".join(liefereinheiten) + ")"
        oereb_sql = "SELECT EBECODE, FILTER_FIELD, FILTER_TYPE FROM GPR WHERE GPRCODE='OEREB'"
        oereb_ebenen = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], oereb_sql)
        for oereb_ebene in oereb_ebenen:
            oereb_table = oereb_ebene[0]
            oereb_liefereinheit_field = oereb_ebene[1]
            oereb_delete_sql = "DELETE FROM %s WHERE %s IN %s" % (oereb_table, oereb_liefereinheit_field, liefereinheiten_joined)
            logger.info("Deleting Transferstruktur neu...")
            logger.info(oereb_delete_sql)
            oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_TEAM']['connection_string'], oereb_delete_sql)
            
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
        
        # GeoDB-Tabellen schreiben (Flag, Task)
        # sowie GeoDB-Taskid in die TICKET-Tabelle zurückschreiben
        #TODO: Workbench so anpassen, dass auch mehrere Geoprodukte pro Ticket korrekt verarbeitet werden. 
        fme_script = os.path.splitext(__file__)[0] + "_geodb.fmw"
        fme_logfile = oerebLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory']) 
        logger.info("Script " +  fme_script + " wird ausgeführt.")
        logger.info("Das FME-Logfile heisst: " + fme_logfile)
        runner = fmeobjects.FMEWorkspaceRunner()
        # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
        # Daher müssen workspace und parameters umgewandelt werden!
        parameters = {
            'WORK_DB': str(config['OEREB2_WORK']['database']),
            'WORK_USERNAME': str(config['OEREB2_WORK']['username']),
            'WORK_PASSWORD': str(config['OEREB2_WORK']['password']),
            'TEAM_DB': str(config['GEODB_DD_TEAM']['database']),
            'TEAM_USERNAME': str(config['GEODB_DD_TEAM']['username']),
            'TEAM_PASSWORD': str(config['GEODB_DD_TEAM']['password']),
            'ART_CLAUSE': str(valid_art),
            'LOGFILE': str(fme_logfile)
        }
        try:
            runner.runWithParameters(str(fme_script), parameters)
        except fmeobjects.FMEException as ex:
            logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
            logger.error(ex)
            logger.error("Release wird abgebrochen!")
            sys.exit()
        
        # Mapfiles kopieren
        logger.info("Mapfiles werden kopiert (oerebpruef->oereb)...")
        release_mapfiles(config, logger)
        
        # Ticket-Status aktualisieren
        logger.info("Ticket-Stati werden aktualisiert.")
        ilader_tasks = set()
        for ticket in tickets:
            # iLader-Task ermitteln (sofern vorhanden)
            # Anpassen, dass der Fall mit mehreren Geoprodukten pro Ticket auch korrekt verarbeitet wird.
            sql_iLader_task = "SELECT task_id_geodb FROM ticket where id=" + unicode(ticket[0])
            taskid = oerebLader.helpers.sql_helper.readSQL(config['OEREB2_WORK']['connection_string'], sql_iLader_task)[0][0]
            if taskid is not None:
                ilader_tasks.add(unicode(taskid))
            else:
                logger.warn("Für das Ticket Nr. " + unicode(ticket[0]) + " wurde kein iLader-Task angelegt.")
                logger.warn("Dieses Ticket bzw. dessen Geoprodukt muss über die reguläre Triggerfunktion importiert werden.")
                
            logger.info("Ticket-Status des Tickets " + unicode(ticket[0]) + " wird auf 4 gesetzt!")
            sql_update_ticket_status = "UPDATE ticket SET status=4 WHERE id=" + unicode(ticket[0])
            try:
                oerebLader.helpers.sql_helper.writeSQL(config['OEREB2_WORK']['connection_string'], sql_update_ticket_status)
            except Exception as ex:
                logger.error("Fehler beim Updaten des Ticket-Status!")
                logger.error(unicode(ex))
                logger.error("Script wird abgebrochen!")
                sys.exit()
        
        logger.warn("Folgende iLader-Tasks müssen nun importiert werden:")
        for iLader_task in ilader_tasks:
            logger.warn("iLader run " + iLader_task)

    # Connection-Files löschen
    oerebLader.helpers.connection_helper.delete_connection_files(config['GEODB_WORK']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['OEREB2_WORK']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['NORM_TEAM']['connection_file'], logger)
    oerebLader.helpers.connection_helper.delete_connection_files(config['OEREB2_TEAM']['connection_file'], logger)
            
    logger.info("Alle Ticket-Stati aktualisiert.")
    logger.info("Release abgeschlossen.")
    