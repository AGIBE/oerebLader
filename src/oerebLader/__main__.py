# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from oerebLader import __version__
import oerebLader.workflows.workflow
import oerebLader.release.release
import oerebLader.refresh_verschnitt.refresh_verschnitt
import oerebLader.refresh_statistics.refresh_statistics
import oerebLader.sync_avdate.sync_avdate
import oerebLader.create_qaspecs.create_qaspecs
import oerebLader.switch_bfsnr.switch_bfsnr
import oerebLader.build_mapfile_kanton.build_mapfile_kanton
import oerebLader.build_map.build_map
import oerebLader.collect_legends.collect_legends
import oerebLader.create_legend.create_legend
import oerebLader.download_tickets.download_tickets
import oerebLader.update_municipality.update_municipality
import oerebLader.repair_geometries.repair_geometries
import oerebLader.update_office.update_office
import oerebLader.check_bundesthemen.check_bundesthemen

def get_open_tickets():
    config = oerebLader.config.get_config()
    # tagesaktuelle Tickets (ART=5) werden hier nicht angezeigt, da sie nicht manuell importiert werden.
    open_tickets_sql = "select ticket.id, ticket.name, ticket.LIEFEREINHEIT, liefereinheit.name from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.ID where ticket.STATUS=1 and ticket.ART IN (1,2,3,4) order by ticket.id"
    open_tickets = config['OEREB_WORK_PG']['connection'].db_read(open_tickets_sql)
  
    ticket_list = []
    
    for open_ticket in open_tickets:
        print(open_ticket)
        print(type(open_ticket[0]))
        print(type(open_ticket[1]))
        print(type(open_ticket[2]))
        print(type(open_ticket[3]))
        ticket_string = "%s (%s) -- %s (%s)" % (unicode(open_ticket[0]), open_ticket[1], open_ticket[3], unicode(open_ticket[2]))
        ticket_list.append(ticket_string)
        
    return ticket_list

def get_releasable_tickets():
    config = oerebLader.config.get_config()
    # tagesaktuelle Tickets (ART=5) werden hier nicht angezeigt, da sie nicht manuell importiert werden.
    open_tickets_sql = "select ticket.id, ticket.name, ticket.LIEFEREINHEIT, liefereinheit.name from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.ID where ticket.STATUS=3 and ticket.ART IN (1,2,3,4) order by ticket.id"
    open_tickets = config['OEREB_WORK_PG']['connection'].db_read(open_tickets_sql)
    
    ticket_list = []
    
    for open_ticket in open_tickets:
        ticket_string = "%s (%s) -- %s (%s)" % (unicode(open_ticket[0]), open_ticket[1], open_ticket[3], unicode(open_ticket[2]))
        ticket_list.append(ticket_string)
        
    return ticket_list

def import_ticket(args):
    oerebLader.workflows.workflow.run_workflow(args.TICKET)
    print("Workflow SUCCESSFUL!")


def list_tickets(args):
    ticket_list = get_open_tickets()
    if len(ticket_list) == 0:
        print("Keine offenen Tickets vorhanden!")
    else:
        for ticket in ticket_list:
            print(ticket)


def list_releaseable_tickets(args):
    ticket_list = get_releasable_tickets()
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


def switch_bfsnr(args):
    oerebLader.switch_bfsnr.switch_bfsnr.run_switch_bfsnr(args.BFSNR)
    print("Switch_bfsnr SUCCESSFUL!")


def build_mapfile_kanton(args):
    oerebLader.build_mapfile_kanton.build_mapfile_kanton.run_build_mapfile_kantonr(
    )
    print("Build_mapfile_kanton SUCCESSFUL!")


def build_map(args):
    oerebLader.build_map.build_map.run_build_map(args.MODE, args.batchdir)
    print("Build_map SUCCESSFUL!")


def collect_legends(args):
    oerebLader.collect_legends.collect_legends.run_collect_legends()
    print("Collect_legends SUCCESSFUL!")


def create_legend(args):
    oerebLader.create_legend.create_legend.run_create_legend(
        args.BFSNR, args.MODE
    )
    print("Create_legend SUCCESSFUL!")


def download_tickets(args):
    oerebLader.download_tickets.download_tickets.run_download_tickets()
    print("Download_Tickets SUCCESSFUL!")


def update_municipality(args):
    oerebLader.update_municipality.update_municipality.run_update_municipality(
        args.SOURCE, args.TARGET
    )
    print("Update_Municipality SUCCESSFUL!")

def repair_geometries(args):
    oerebLader.repair_geometries.repair_geometries.run_repair_geometries(args.TARGET)
    print("Repair_geometries SUCCESSFUL!")

def update_office(args):
    oerebLader.update_office.update_office.run_update_office(args.TARGET)
    print("Update_office SUCCESSFUL!")

def check_bundesthemen(args):
    oerebLader.check_bundesthemen.check_bundesthemen.run_check_bundesthemen()
    print("Check Bundesthemen SUCCESSFUL!")

def main():
    version_text = "oerebLader v" + __version__
    parser = argparse.ArgumentParser(
        description="Kommandozeile fuer den oerebLader. Importiert Tickets und zeigt offene Tickets an.",
        prog="oerebLader.exe",
        version=version_text
    )
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')

    # LIST-Befehl
    list_parser = subparsers.add_parser(
        'list', help='zeigt alle importierbaren Tickets an.'
    )
    list_parser.set_defaults(func=list_tickets)

    # LIST_RELEASE-Befehl
    list_release_parser = subparsers.add_parser(
        'list_release', help='zeigt alle zum Release bereiten Tickets an.'
    )
    list_release_parser.set_defaults(func=list_releaseable_tickets)

    # IMPORT-Befehl
    import_parser = subparsers.add_parser(
        'import', help='importiert das angegebene Ticket.'
    )
    import_parser.add_argument(
        "TICKET", type=int, help="auszufuehrendes Ticket."
    )
    import_parser.set_defaults(func=import_ticket)

    # RELEASE-Befehl
    release_parser = subparsers.add_parser(
        'release',
        help='gibt alle anerkannten, nicht tagesaktuellen Tickets frei.'
    )
    release_parser.set_defaults(func=release)

    # RELEASE_DAILY-Befehl
    release_daily_parser = subparsers.add_parser(
        "release_tagesaktuell", help='gibt alle tagesaktuellen Tickets frei.'
    )
    release_daily_parser.set_defaults(func=release_daily)

    # REFRESH_STATISTICS-Befehl
    refresh_statistics_parser = subparsers.add_parser(
        "refresh_statistics",
        help='Aktualisiert die Oracle-Statistiken des OEREB-Schemas in VEK1 und VEK2.'
    )
    refresh_statistics_parser.set_defaults(func=refresh_statistics)

    # REFRESH_VERSCHNITT-Befehl
    refresh_verschnitt_parser = subparsers.add_parser(
        "refresh_verschnitt",
        help='Liest die Dictionary Caches sowie die Config der Verschnittfunktion neu ein.'
    )
    refresh_verschnitt_parser.set_defaults(func=refresh_verschnitt)

    # SYNC_AVDATE-Befehl
    sync_avdate_parser = subparsers.add_parser(
        "sync_avdate",
        help="Kopiert das MOPUBE-Nachführungsdatum aus dem GeoDB-DD in die Konfig der ÖREBK-Verschnittfunktion."
    )
    sync_avdate_parser.set_defaults(func=sync_avdate)

    # CREATE_QASPECS-Befehl
    create_qaspecs_parser = subparsers.add_parser(
        "create_qaspecs",
        help="Erstellt pro Liefereinheit ein QA-Spezifikations-XML."
    )
    create_qaspecs_parser.set_defaults(func=create_qaspecs)

    # SWITCH_BFSNR-Befehl
    switch_bfsnr_parser = subparsers.add_parser(
        "switch_bfsnr",
        help="Wechselt den Gemeinde-Prüfdienst auf eine neue Gemeinde."
    )
    switch_bfsnr_parser.add_argument(
        "BFSNR",
        type=int,
        choices=range(300, 999),
        help="BFSNR der Gemeinde, auf die das Mapfile wechseln soll."
    )
    switch_bfsnr_parser.set_defaults(func=switch_bfsnr)

    # BUILD_MAPFILE_KANTON-Befehl
    build_mapfile_kanton_parser = subparsers.add_parser(
        "build_mapfile_kanton",
        help="Erstellt das Mapfile für den Kantons-Prüfdienst neu."
    )
    build_mapfile_kanton_parser.set_defaults(func=build_mapfile_kanton)

    # BUILD_MAP-Befehl
    build_map_parser = subparsers.add_parser(
        "build_map",
        help="Erstellt das Mapfile für den öffentlichen Dienst (VEK1), den Vorschaudienst (VEK2) den Prüfdienst (WORK)."
    )
    build_map_parser.add_argument(
        "MODE",
        choices=[
            "oereb", "oerebpreview", "oerebpruef", "oerebav", "oerebhinweis"
        ],
        help="Zu erstellendes Mapfile (oereb, oerebpreview, oerebpruef, oerebav oder oerebhinweis)."
    )
    build_map_parser.add_argument(
        "batchdir",
        help="Verzeichnis, in dem der publish-Batch erstellt werden soll."
    )
    build_map_parser.set_defaults(func=build_map)

    # COLLECT_LEGENDS-Befehl
    collect_legends_parser = subparsers.add_parser(
        "collect_legends",
        help="Sucht die aktuellen Gemeinde-Legenden zusammen und kopiert sie in den Legenden-Ordner."
    )
    collect_legends_parser.set_defaults(func=collect_legends)

    # CREATE_LEGEND-Befehl
    create_legend_parser = subparsers.add_parser(
        "create_legend",
        help="Erstellt die HTML-Legenden neu. Entweder für alle aufgeschalteten Gemeinden oder nur für eine einzelne aufgeschaltete Gemeinde."
    )
    valid_bfsnr = range(300, 1000)
    valid_bfsnr = map(unicode, valid_bfsnr)
    valid_bfsnr.append("ALL")
    create_legend_parser.add_argument(
        "BFSNR",
        choices=valid_bfsnr,
        nargs='?',
        help="BFSNR der Gemeinde, deren HTML-Legende aktualisiert werden soll."
    )
    create_legend_parser.add_argument(
        "MODE",
        choices=['oereb', 'oerebpruef'],
        help="Welche Legende soll erstellt werden? Prüflegende (oerebpruef) oder öffentliche Legende (oereb)."
    )
    create_legend_parser.set_defaults(func=create_legend)

    # DOWNLOAD_TICKETS-Befehl
    download_tickets_parser = subparsers.add_parser(
        "download_tickets",
        help="Lädt die aktuellen Ticketlisten aus dem Ticketsystem herunter."
    )
    download_tickets_parser.set_defaults(func=download_tickets)

    # UPDATE_MUNICIPALITY-Befehl
    update_municipality_parser = subparsers.add_parser(
        "update_municipality",
        help="Aktualisiert die Municipality-Tabelle in der PostGIS-Transferstruktur."
    )
    update_municipality_parser.add_argument(
        "TARGET",
        choices=['work', 'team', 'vek2', 'vek1'],
        help="In welche Datenbank soll aktualisiert werden?"
    )
    update_municipality_parser.add_argument(
        "SOURCE",
        choices=[
            'GENGRZ5_GENG5', 'GENGRZ5_GEN2G5', 'GENGRZ5_GEN3G5',
            'GENGRZ5_GEN4G5'
        ],
        help="Aus welcher Quelle soll aktualisiert werden?"
    )
    update_municipality_parser.set_defaults(func=update_municipality)

    # REPAIR_GEOMETRIES-Befehl
    repair_geometries_parser = subparsers.add_parser("repair_geometries", help="Repariert in allen PostGIS-Schemas die Geometrien mit ST_MAKEVALID().")
    repair_geometries_parser.add_argument("TARGET", choices=['work', 'team', 'vek2', 'vek1'], help="In welcher Datenbank soll repariert werden?")
    repair_geometries_parser.set_defaults(func=repair_geometries)

    # UPDATE_OFFICE-Befehl
    update_office_parser = subparsers.add_parser("update_office", help="Aktualisiert alle Office-Tabellen aus der zentralen AMT-Tabelle.")
    update_office_parser.add_argument("TARGET", choices=['work', 'team', 'vek2', 'vek1'], help="In welcher Datenbank soll aktualisiert werden?")
    update_office_parser.set_defaults(func=update_office)

    # CHECK_BUNDESTHEMEN-Befehl
    check_bundesthemen_parser = subparsers.add_parser("check_bundesthemen", help="Prüft für alle Bundesthemen, ob eine Aktualisierung vorliegt.")
    check_bundesthemen_parser.set_defaults(func=check_bundesthemen)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()