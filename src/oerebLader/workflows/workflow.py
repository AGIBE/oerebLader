# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.config
import oerebLader.workflows.w2_kbs
import oerebLader.workflows.w1_gsk
import oerebLader.workflows.w3_tba
import oerebLader.workflows.w4_npl
import oerebLader.workflows.w5_nplbern
import oerebLader.workflows.w6_nplkueo
import oerebLader.workflows.w7_nplwald
import oerebLader.workflows.w8_kbsoev
import oerebLader.workflows.w9_kbsflug
import oerebLader.workflows.w10_sizoplan
import oerebLader.workflows.w11_prjzflug
import oerebLader.workflows.w12_nplwald_bern
import oerebLader.workflows.w13_baulnstr
import oerebLader.workflows.w14_ggo
import oerebLader.workflows.w15_gbo
import oerebLader.workflows.w16_nsg
import oerebLader.workflows.w17_kbsmil
import sys

def run_workflow(ticketnr):
    config = oerebLader.config.get_config()
    if is_valid_ticket(ticketnr, config):
        print("Fuehre aus: " + unicode(ticketnr))
        workflow = get_workflow_for_ticket(ticketnr, config)
        if workflow != "":
            print("Fuehre den Workflow " + workflow + " aus.")
            modul = "oerebLader.workflows." + workflow
            m = sys.modules["oerebLader.workflows." + workflow]
            m.run(ticketnr)
        else:
            print("Fuer das Ticket " + unicode(ticketnr) + " konnte kein Workflow gefunden werden.")
            print("Der Import wird nicht ausgefuehrt.")
    else:
        print("Die angegebene Ticket-Nummer ist ungueltig.")
        print("Der Import wird nicht ausgefuehrt.")
        raise ValueError("Die angegebene Ticket-Nummer ist ungueltig.")

def is_valid_ticket(ticketnr, config):

    valid_ticket = False

    valid_ticket_sql = "SELECT id, status FROM ticket WHERE id=" + unicode(ticketnr)
    results = config['OEREB_WORK_PG']['connection'].db_read(valid_ticket_sql)

    if len(results) == 1:
        status = results[0][1]
        if status == 1:
            valid_ticket = True

    return valid_ticket

def get_workflow_for_ticket(ticketnr, config):
    workflow_ticket_sql = "select ticket.id, liefereinheit.WORKFLOW from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.ID where ticket.ID=" + unicode(ticketnr)

    results = config['OEREB_WORK_PG']['connection'].db_read(workflow_ticket_sql)

    workflow = ""

    if len(results) == 1:
        workflow = results[0][1]

    return workflow
