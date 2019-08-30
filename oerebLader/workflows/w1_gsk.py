# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s13_import_gsk
import oerebLader.scripts.s42_derive_gsk25_transfer
import oerebLader.scripts.s67_update_data_integration
import oerebLader.scripts.s27_qa_gsk25
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s13_import_gsk.run(config)
    oerebLader.scripts.s42_derive_gsk25_transfer.run(config)
    oerebLader.scripts.s67_update_data_integration.run(config)
    oerebLader.scripts.s27_qa_gsk25.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)