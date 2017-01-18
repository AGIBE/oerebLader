# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s1_delete_npl
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s52_import_nupla_bern
import oerebLader.scripts.s17_import_npl
import oerebLader.scripts.s9_derive_npl_transfer
import oerebLader.scripts.s50_create_legend
import oerebLader.scripts.s31_qa_npl
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s1_delete_npl.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s52_import_nupla_bern(config)
    oerebLader.scripts.s17_import_npl.run(config)
    oerebLader.scripts.s9_derive_npl_transfer.run(config)
    oerebLader.scripts.s50_create_legend.run(config)
    oerebLader.scripts.s31_qa_npl.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)