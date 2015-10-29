# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper
import oerebLader.workflows.w8_kbsoev
import oerebLader.workflows.w9_kbsflug
import oerebLader.workflows.w10_sizoplan
import oerebLader.workflows.w11_prjzflug
import sys

def run_workflow(ticketnr):
    config = oerebLader.helpers.config.get_config()
    if is_valid_ticket(ticketnr, config):
        print("Führe aus: " + unicode(ticketnr))
        workflow = get_workflow_for_ticket(ticketnr, config)
        if workflow != "":
            print("Führe den Workflow " + workflow + " aus.")
            modul = "oerebLader.workflows." + workflow
            m = sys.modules["oerebLader.workflows." + workflow]
            m.run(ticketnr)
        else:
            print("Für das Ticket " + unicode(ticketnr) + " konnte kein Workflow gefunden werden.")
            print("Der Import wird nicht ausgeführt.")
    else:
        print("Die angegebene Ticket-Nummer ist ungültig.")
        print("Der Import wird nicht ausgeführt.")

def is_valid_ticket(ticketnr, config):
    
    valid_ticket = False
    
    valid_ticket_sql = "SELECT id, status FROM ticket WHERE id=" + unicode(ticketnr)
    results = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], valid_ticket_sql)
    
    if len(results) == 1:
        status = results[0][1]
        if status == 1:
            valid_ticket = True
    
    return valid_ticket

def get_workflow_for_ticket(ticketnr, config):
    workflow_ticket_sql = "select ticket.id, liefereinheit.WORKFLOW from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.ID where ticket.ID=" + unicode(ticketnr)
    
    results = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], workflow_ticket_sql)
    
    workflow = ""
    
    if len(results) == 1:
        workflow = results[0][1]
        
    return workflow
    