# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s15_import_kbsbund
import oerebLader.scripts.s24_import_transfer_xtf
import oerebLader.scripts.s29_qa_kbsflug
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

ticketnr = 3

config = oerebLader.helpers.config.get_config(ticketnr)

oerebLader.scripts.s26_initialize.run(config, ticketnr)
oerebLader.scripts.s4_delete_transfer.run(config)
oerebLader.scripts.s15_import_kbsbund.run(config)
oerebLader.scripts.s24_import_transfer_xtf.run(config)
oerebLader.scripts.s29_qa_kbsflug.run(config)
oerebLader.scripts.s38_qa_transfer.run(config)
oerebLader.scripts.s12_finish.run(config)

print("Workflow fertig!")