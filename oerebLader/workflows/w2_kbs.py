# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s14_import_kbs
import oerebLader.scripts.s41_derive_kbs_transfer
import oerebLader.scripts.s67_update_data_integration
import oerebLader.scripts.s28_qa_kbs
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s14_import_kbs.run(config)
    oerebLader.scripts.s41_derive_kbs_transfer.run(config)
    oerebLader.scripts.s67_update_data_integration.run(config)
    oerebLader.scripts.s28_qa_kbs.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)