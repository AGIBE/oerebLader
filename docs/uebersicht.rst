Übersicht über die Applikation
==============================
Der oerebLader besteht aus verschiedenen Modulen:

Bundesthemen prüfen
-------------------
Die ÖREBK-Themen in alleiniger Zuständigkeit Bund werden über die Plattform http://data.geo.admin.ch zum Download angeboten. Da kein Meldewesen bezüglich Aktualisierungen existiert, muss täglich geprüft werden, ob eines der Themen aktualisiert worden ist. Genau dieser Vorgang wird mit diesem Modul ausgeführt. Sofern ein Datensatz aktualisiert wurde, wird für ihn ein Eintrag in der Tabelle TICKET erstellt. Dadurch kann er mit der Import-Funktion (s. unten) importiert werden.

Die Prüfung, ob eine Aktualisierung vorliegt, wird mit einer MD5-Checksumme gemacht. Die MD5-Checksumme des aktuellsten Datensatzes ist auf http://data.geo.admin.ch in der ZIP-Datei abgelegt. Sie wird mit der in der Tabelle LIEFEREINHEIT gespeicherten MD5-Prüfsumme des im ÖREB-Kataster vorgehaltenen Datensatzes verglichen. Stimmen die beiden Prüfsummen nicht überein, handelt es sich um eine Aktualisierung.  

Import
------

Workflows
^^^^^^^^^
- w1 - w13
Scripts
^^^^^^^
- s1 - s40

Release
-------
- Sammelfunktion für alle Tickets mit Status=3 (anerkannt)
- kopiert Geoprodukte und Transferstruktur von WORK nach TEAM
- ändert Ticketstatus (=4)
- schreibt Einträge in Import-Tabelle iLader

Konfiguration
-------------
Der oerebLader bezieht seine Konfiguration aus einer zentralen-Konfigurationsdatei namens ``config.ini``. Der Ort der Konfigurationsdatei wird über die Umgebungsvariable ``OEREBIMPORTHOME`` bestimmt.