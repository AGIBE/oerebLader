Installationsanleitung
======================

Systemvoraussetzungen
---------------------
- ArcGIS Desktop 10.2.2 (inkl. Python 2.7.5)
- Oracle Client 32bit 11.2.0.x
- FME Desktop 2014 SP4
- ESRI QA Framework 10.2.*

Requirements
------------
- arcpy (wird durch ArcGIS Desktop bereitgestellt; inkl. numpy)
- cx-Oracle (ist Teil des kantonalen GIS-Arbeitsplatzes)
- python-keyczar (inkl. pycrypto)
- configobj
- chromalog

Berechtigungen
--------------
- lesender Zugriff auf das zentrale Config-File (definiert in ``OEREBIMPORTHOME``)
- lesender Zugriff auf Schlüsselablage (definiert in ``OEREBIMPORTSECRET``)
- lesender Zugriff auf Datenverzeichnisse (definiert in Tabelle ``LIEFEREINHEIT``)
- schreibender Zugriff auf das Log-Verzeichnis (definiert in zentralem Config-File)

Neuinstallation
---------------
#. Installation pycrypto

   * pycrypto kann nicht mit pip installiert werden, da das Paket dabei kompiliert wird. Die notwendigen Compiler-Tools sind aber auf den PCs nicht installiert. Deshalb muss eine kompilierte Version via Setup installiert werden.
   * exe ausführen. Vorkompilierte Binaires gibt es hier: http://www.voidspace.org.uk/python/modules.shtml#pycrypto
   * richtige Python-Installation auswählen

#. Installation pip

   * ``python get-pip.py``
   * Umgebungsvariable PATH ergänzen um Pfad zum Python-Binary (``C:\Prog\Python27\ArcGIS10.2``).
   * Umgebungsvariable PATH ergänzen um Pfad zum oerebLader.exe und pip.exe (``C:\Prog\Python27\ArcGIS10.2\Scripts``).

#. Installation oerebLader

   * ``pip install oerebLader-x.x-py2-none-any.whl``
   * damit werden die übrigen Requirements automatisch mitinstalliert.

#. Konfiguration oerebLader

   * Umgebungsvariable ``OEREBIMPORTHOME`` setzen (Freigabe-Share). Dieser Pfad zeigt auf die zentrale Konfigurationsdatei namens ``config.ini``.
   * Umgebungsvariable ``OEREBIMPORTSECRET`` setzen (persönliches Laufwerk). Dieser Pfad zeigt auf die Schlüssel-Dateien, mit denen die Passworte in der zentralen Konfigurationsdatei ent- und verschlüsselt werden.
   * Schlüssel kopieren (Files ``meta`` und ``1``) nach ``OEREBIMPORTSECRET``
   * In der Umgebungsvariable ``PYTHONPATH`` den Pfad zu den fmeobjects in der FME-Installation einfügen (``..\FMEfmeobjects\python27``)

Aktualisierung
--------------

#. oerebLader deinstallieren (``pip uninstall oerebLader``)
#. oerebLader installieren (``pip install oerebLader-x.x-py2-none-any.whl``)
#. Alternative: ``pip install --upgrade oerebLader-x.x-py2-none-any.whl``
#. evtl. Änderungen an Config vornehmen (Connection-Files etc.)
