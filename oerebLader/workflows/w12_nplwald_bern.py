# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s3_delete_nuplwald
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s54_import_nuplwald_bern
import oerebLader.scripts.s66_update_availability
import oerebLader.scripts.s67_update_data_integration
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s56_qa_nuplwald
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s3_delete_nuplwald.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s54_import_nuplwald_bern.run(config)
    oerebLader.scripts.s66_update_availability.run(config)
    oerebLader.scripts.s67_update_data_integration.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s56_qa_nuplwald.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)