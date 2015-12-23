Datenintegration ÖREB-Kataster
==============================
Bei einer Datenintegration werden folgende Elemente importiert:

- Geodaten (=Geoprodukt)
- Transferstruktur (spez. Datenmodell für ÖREB-Kataster)
- Rechtsvorschriften (PDF-Dokumente)

Der Import ist zweigeteilt. In einem ersten Schritt werden die Datenlieferungen mit dem oerebLader aufbereitet und in die DB importiert. In einem zweiten Schritt werden sie dann mit der regulären Import-Software namens iLader in die GeoDB importiert.

Grafik einbauen

Datentöpfe
----------

Produktionssystem
^^^^^^^^^^^^^^^^^
Alle ÖREBK-Themen werden in externen Produktionssystemen durch die zuständigen Stellen produziert. Für jedes Thema ist Format und Ort der Anlieferung definiert und stabil.

WORK
^^^^^
Die importierten Daten liegen in der GeoDB-Instanz WORK, d.h. Geoprodukt und Transferstruktur. 

TEAM
^^^^^
Die anerkannten Daten liegen in der GeoDB-Instanz TEAM, d.h. Geoprodukt und Transferstruktur. 

Freigabe-Bereich GeoDB
^^^^^^^^^^^^^^^^^^^^^^
Die freigegebenen, publizierten Daten liegen in den GeoDB-Instanzen VEK1, VEK2 und VEK3.
 
Internet-Dateiablage
^^^^^^^^^^^^^^^^^^^^
Sämtliche Rechtsvorschriften-Dokumente (Ausnahme: Bundesthemen) liegen in der Internet-Dateiablage.

Grobablauf
----------
Produktion
^^^^^^^^^^
- Produktion zuständige Stelle (extern)
Anlieferung
^^^^^^^^^^^
Import (inkl. Prüfung)
^^^^^^^^^^^^^^^^^^^^^^^
Anerkennung
^^^^^^^^^^^
- Anerkennung durch zuständige Stelle (Hier werden die Daten technisch (mit dem QA-Framework) und fachlich/inhaltlich (per Prüfkarte) geprüft. Die fachlich/inhaltliche Prüfung erfolgt durch die zuständige Stelle (Ausnahme: Bundesthemen) und endet im Erfolgfalls mit der Anerkennung der Daten nach ÖREBKV Art.5.)
Release
^^^^^^^
GeoDB-Import iLader
^^^^^^^^^^^^^^^^^^^
 (s. Dokumenatation iLader)