# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s1_delete_npl
import oerebLader.scripts.s5_delete_uzp
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s17_import_npl
import oerebLader.scripts.s25_import_uzp
import oerebLader.scripts.s40_update_oerebsta
import oerebLader.scripts.s9_derive_npl_transfer
import oerebLader.scripts.s31_qa_npl
import oerebLader.scripts.s39_qa_uzp
import oerebLader.scripts.s35_qa_oerebsta
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

def run(ticketnr):

    config = oerebLader.helpers.config.get_config()
    
    oerebLader.scripts.s26_initialize.run(config, ticketnr)
    oerebLader.scripts.s1_delete_npl.run(config)
    # oerebLader.scripts.s5_delete_uzp.run(config)
    oerebLader.scripts.s4_delete_transfer.run(config)
    oerebLader.scripts.s17_import_npl.run(config)
    # oerebLader.scripts.s25_import_uzp.run(config)
    # oerebLader.scripts.s40_update_oerebsta.run(config)
    oerebLader.scripts.s9_derive_npl_transfer.run(config)
    oerebLader.scripts.s31_qa_npl.run(config)
    # oerebLader.scripts.s39_qa_uzp.run(config)
    # oerebLader.scripts.s35_qa_oerebsta.run(config)
    oerebLader.scripts.s38_qa_transfer.run(config)
    oerebLader.scripts.s12_finish.run(config)