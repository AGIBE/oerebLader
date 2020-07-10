# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s1_delete_nupla
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s48_import_nupla
import oerebLader.scripts.s49_derive_legendenbildli
import oerebLader.scripts.s50_create_legend
import oerebLader.scripts.s66_update_availability
import oerebLader.scripts.s67_update_data_integration
import oerebLader.scripts.s55_qa_nupla
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.config

def run(ticketnr):

    config = oerebLader.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s1_delete_nupla.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s48_import_nupla.run(config)
    oerebLader.scripts.s49_derive_legendenbildli.run(config)
    oerebLader.scripts.s50_create_legend.run(config)
    oerebLader.scripts.s66_update_availability.run(config)
    oerebLader.scripts.s67_update_data_integration.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    # oerebLader.scripts.s55_qa_nupla.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)