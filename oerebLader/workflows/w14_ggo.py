# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s60_import_ggo
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s61_qa_ggo
import oerebLader.scripts.s44_checkurl_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()

    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s60_import_ggo.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s62_qa_ggo.run(config)
    oerebLader.scripts.s44_checkurl_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)