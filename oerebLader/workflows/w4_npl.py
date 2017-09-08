# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s1_delete_nupla
import oerebLader.scripts.s5_delete_uzp
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s51_derive_darstellung
import oerebLader.scripts.s25_import_uzp
import oerebLader.scripts.s40_update_oerebsta
import oerebLader.scripts.s48_import_nupla
import oerebLader.scripts.s49_derive_legendenbildli
import oerebLader.scripts.s50_create_legend
import oerebLader.scripts.s31_qa_npl
import oerebLader.scripts.s39_qa_uzp
import oerebLader.scripts.s35_qa_oerebsta
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s1_delete_nupla.run(config)
    # oerebLader.scripts.s5_delete_uzp.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    # oerebLader.scripts.s25_import_uzp.run(config)
    # oerebLader.scripts.s40_update_oerebsta.run(config)
    oerebLader.scripts.s48_import_nupla.run(config)
    oerebLader.scripts.s51_derive_darstellung.run(config)
    oerebLader.scripts.s49_derive_legendenbildli.run(config)
    oerebLader.scripts.s50_create_legend.run(config)
    oerebLader.scripts.s31_qa_npl.run(config)
    # oerebLader.scripts.s39_qa_uzp.run(config)
    # oerebLader.scripts.s35_qa_oerebsta.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)