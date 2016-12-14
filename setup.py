# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup
from oerebLader import __version__
import oerebLader
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "oerebLader",
      packages = find_packages(),
      version = __version__,
      # .fmw-Files werden von Python nicht erkannt. Deshalb müssen sie explizit als Package-Inhalt aufgelistet werden.
      package_data={'': ["*.fmw"]},
      # Abhängigkeiten
      install_requires = ["configobj==5.0.6", "cx-Oracle==5.1.3", "python-keyczar==0.715", "chromalog==1.0.4", "requests==2.8.0", "chardet==2.3.0", "Jinja2==2.8"],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@bve.be.ch",
      description = "Import-Modul ÖREB-Kataster des Kantons Bern",
      url = "http://www.be.ch/oerebk",
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
         'console_scripts': [
              'checkBundesthemen = oerebLader.helpers.bundesthemen_helper:check_bundesthemen',
              'oerebLader = oerebLader.helpers.commandline_helper:main',
              'ol = oerebLader.helpers.commandline_helper:main'
          ]
    }
)