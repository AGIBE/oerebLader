# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from oerebLader import __version__
import oerebLader.helpers.ticket_helper
import oerebLader.workflows.workflow
import oerebLader.release.release
import oerebLader.refresh_verschnitt.refresh_verschnitt

def import_ticket(args):
    oerebLader.workflows.workflow.run_workflow(args.TICKET)
    print("Workflow SUCCESSFUL!")

def list_tickets(args):
    ticket_list = oerebLader.helpers.ticket_helper.get_open_tickets()
    if len(ticket_list) == 0:
        print("Keine offenen Tickets vorhanden!")
    else:
        for ticket in ticket_list:
            print(ticket)
            
def release(args):
    oerebLader.release.release.run_release(False)
    print("Release SUCCESSFUL!")
    
def release_daily(args):
    oerebLader.release.release.run_release(True)
    print("Release Tagesaktuell SUCCESSFUL!")
    
def refresh_verschnitt(args):
    oerebLader.refresh_verschnitt.refresh_verschnitt.run_refresh_verschnitt()
    print("Refresh_Verschnitt SUCCESSFUL!")

def main():
    version_text = "oerebLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den oerebLader. Importiert Tickets und zeigt offene Tickets an.", prog="oerebLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle importierbaren Tickets an.')
    list_parser.set_defaults(func=list_tickets)
    
    # IMPORT-Befehl
    import_parser = subparsers.add_parser('import', help='importiert das angegebene Ticket.')
    import_parser.add_argument("TICKET", type=int, help="auszufuehrendes Ticket.")
    import_parser.set_defaults(func=import_ticket)
    
    # RELEASE-Befehl
    release_parser = subparsers.add_parser('release', help='gibt alle anerkannten, nicht tagesaktuellen Tickets frei.')
    release_parser.set_defaults(func=release)
    
    # RELEASE_DAILY-Befehl
    release_daily_parser = subparsers.add_parser("release_tagesaktuell", help='gibt alle tagesaktuellen Tickets frei.')
    release_daily_parser.set_defaults(func=release_daily)
    
    # REFRESH_VERSCHNITT-Befehl
    refresh_verschnitt_parser = subparsers.add_parser("refresh_verschnitt", help='Liest die Dictionary Caches sowie die Config der Verschnittfunktion neu ein.')
    refresh_verschnitt_parser.set_defaults(func=refresh_verschnitt)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()