# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import chromalog

def create_loghandler_stream():
    '''
    Konfiguriert einen Stream-Loghandler. Der Output
    wird in sys.stdout ausgegeben. In der Regel ist das
    die Kommandozeile. Falls sys.stdout dies unterst�tzt,
    werden Warnungen und Fehler farbig ausgegeben (dank
    des chromalog-Moduls).
    '''
    
    file_formatter = chromalog.ColorizingFormatter('%(levelname)s|%(message)s')
    
    h = chromalog.ColorizingStreamHandler()
    h.setLevel(logging.DEBUG)
    h.setFormatter(file_formatter)
    
    return h
    
def create_loghandler_file(filename):
    '''
    Konfiguriert einen File-Loghandler
    :param filename: Name (inkl. Pfad) des Logfiles 
    '''
    
    file_formatter = logging.Formatter('%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', '%Y-%m-%d %H:%M:%S')
    
    h = logging.FileHandler(filename, encoding="UTF-8")
    h.setLevel(logging.DEBUG)
    h.setFormatter(file_formatter)
    
    return h