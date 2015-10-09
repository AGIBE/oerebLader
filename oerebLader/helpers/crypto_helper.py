# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import keyczar.keyczar
import os

class Crypter(object):
    '''
    Hilfsklasse für die Ent- und Verschlüsselung der Passwörter
    inspiriert durch: https://code.google.com/p/keyczar/wiki/SamplePythonUsage
    Die Schlüssel werden mit dem Keyczar-Tool (jar-File) erzeugt
    '''
    
    @staticmethod
    def _read(loc):
        '''
        statische Methode, die den Schlüssel einliest
        :param loc: Ordner, in dem der Schlüssel liegt
        '''
        return keyczar.keyczar.Crypter.Read(loc)
    
    def __init__(self):
        '''
        Konstruktor
        '''
        self.key_directory = os.environ['OEREBIMPORTSECRET']
        
        self.crypt = self._read(self.key_directory)
        
    def encrypt(self, data):
        '''
        verschlüsselt den übergebenen String
        
        :param data: zu verschlüsselnder String
        '''
        return self.crypt.Encrypt(data)
    
    def decrypt(self, data):
        '''
        entschlüsselt den übergebenen String
        
        :param data: zu entschlüsselnder String
        '''
        return self.crypt.Decrypt(data).decode("iso-8859-1")