# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime

def prepare_fme_log(fme_script, log_directory):
    prefix = os.path.splitext(os.path.basename(fme_script))[0]
    fme_logfilename = prefix + ".log"
    fme_logfile = os.path.join(log_directory, fme_logfilename)
    
    if os.path.exists(fme_logfile):
        archive_logfilename = prefix + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
        archive_logfile = os.path.join(log_directory, archive_logfilename)
        os.rename(fme_logfile, archive_logfile)
        
    return fme_logfile