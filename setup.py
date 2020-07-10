# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
      name = "oerebLader",
      packages = find_packages(where="src"),
      version = get_version("src/oerebLader/__init__.py"),
      # .fmw-Files werden von Python nicht erkannt. Deshalb müssen sie explizit als Package-Inhalt aufgelistet werden.
      package_data={'': ["*.fmw"]},
      package_dir = {"": "src"},
      # Abhängigkeiten
      install_requires = ["AGILib>=1.1"],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@be.ch",
      description = "Import-Modul ÖREB-Kataster des Kantons Bern",
      url = "http://www.be.ch/oerebk",
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
         'console_scripts': [
              'oerebLader = oerebLader.__main__:main',
              'ol = oerebLader.__main__:main'
          ]
    }
)