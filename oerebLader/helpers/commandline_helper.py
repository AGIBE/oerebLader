# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from oerebLader import __version__
import oerebLader.helpers.ticket_helper
import oerebLader.workflows.workflow

def run_ticket(args):
    oerebLader.workflows.workflow.run_workflow(args.TICKET)

def list_tickets(args):
    ticket_list = oerebLader.helpers.ticket_helper.get_open_tickets()
    if len(ticket_list) == 0:
        print("Keine offenen Tickets vorhanden!")
    else:
        for ticket in ticket_list:
            print(ticket)

def main():
    version_text = "oerebLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den oerebLader. Importiert Tickets und zeigt offene Tickets an.", prog="oerebLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle importierbaren Tickets an.')
    list_parser.set_defaults(func=list_tickets)
    
    # RUN-Befehl
    run_parser = subparsers.add_parser('run', help='importiert das angegebene Ticket.')
    run_parser.add_argument("TICKET", type=int, help="auszufuehrendes Ticket.")
    run_parser.set_defaults(func=run_ticket)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()