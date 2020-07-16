# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s15_import_kbsbund
import oerebLader.scripts.s24_import_transfer_xtf
import oerebLader.scripts.s67_update_data_integration
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.config

def run(ticketnr):

    config = oerebLader.config.get_config()

    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s15_import_kbsbund.run(config)
    oerebLader.scripts.s24_import_transfer_xtf.run(config)
    oerebLader.scripts.s67_update_data_integration.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)