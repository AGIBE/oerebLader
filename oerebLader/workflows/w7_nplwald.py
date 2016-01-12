# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s3_delete_nplwald
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s21_import_nplwald
import oerebLader.scripts.s11_derive_nplwald_transfer
import oerebLader.scripts.s34_qa_nplwald
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s3_delete_nplwald.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s21_import_nplwald.run(config)
    oerebLader.scripts.s11_derive_nplwald_transfer.run(config)
    oerebLader.scripts.s34_qa_nplwald.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)