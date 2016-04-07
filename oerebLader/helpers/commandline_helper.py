# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from oerebLader import __version__
import oerebLader.helpers.ticket_helper
import oerebLader.workflows.workflow
import oerebLader.release.release
import oerebLader.refresh_verschnitt.refresh_verschnitt
import oerebLader.refresh_statistics.refresh_statistics
import oerebLader.sync_avdate.sync_avdate
import oerebLader.create_qaspecs.create_qaspecs

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
            
def list_releaseable_tickets(args):
    ticket_list = oerebLader.helpers.ticket_helper.get_releasable_tickets()
    if len(ticket_list) == 0:
        print("Keine Tickets zum Release bereit!")
    else:
        print("Folgende Tickets werden mit 'oerebLader release' freigegeben.")
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
    
def refresh_statistics(args):
    oerebLader.refresh_statistics.refresh_statistics.run_refresh_statistics()
    print("Refresh_Statistics SUCCESSFUL!")
    
def sync_avdate(args):
    oerebLader.sync_avdate.sync_avdate.run_sync_avdate()
    print("Sync_avdate SUCCESSFUL!")
    
def create_qaspecs(args):
    oerebLader.create_qaspecs.create_qaspecs.run_create_qaspecs()
    print("Create_qaspces SUCCESSFUL!")

def main():
    version_text = "oerebLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den oerebLader. Importiert Tickets und zeigt offene Tickets an.", prog="oerebLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle importierbaren Tickets an.')
    list_parser.set_defaults(func=list_tickets)

    # LIST_RELEASE-Befehl
    list_release_parser = subparsers.add_parser('list_release', help='zeigt alle zum Release bereiten Tickets an.')
    list_release_parser.set_defaults(func=list_releaseable_tickets)
    
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
    
    # REFRESH_STATISTICS-Befehl
    refresh_statistics_parser = subparsers.add_parser("refresh_statistics", help='Aktualisiert die Oracle-Statistiken des OEREB-Schemas in VEK1 und VEK2.')
    refresh_statistics_parser.set_defaults(func=refresh_statistics)

    # REFRESH_VERSCHNITT-Befehl
    refresh_verschnitt_parser = subparsers.add_parser("refresh_verschnitt", help='Liest die Dictionary Caches sowie die Config der Verschnittfunktion neu ein.')
    refresh_verschnitt_parser.set_defaults(func=refresh_verschnitt)
    
    # SYNC_AVDATE-Befehl
    sync_avdate_parser = subparsers.add_parser("sync_avdate", help="Kopiert das MOPUBE-Nachführungsdatum aus dem GeoDB-DD in die Konfig der ÖREBK-Verschnittfunktion.")
    sync_avdate_parser.set_defaults(func=sync_avdate)
    
    # CREATE_QASPECS-Befehl
    create_qaspecs_parser = subparsers.add_parser("create_qaspecs", help="Erstellt pro Liefereinheit ein QA-Spezifikations-XML.")
    create_qaspecs_parser.set_defaults(func=create_qaspecs)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()