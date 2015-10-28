# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s23_import_sizoplan
import oerebLader.scripts.s24_import_transfer_xtf
import oerebLader.scripts.s37_qa_sizoplan
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

ticketnr = 5

config = oerebLader.helpers.config.get_config()

oerebLader.scripts.s26_initialize.run(config, ticketnr)
oerebLader.scripts.s4_delete_transfer.run(config)
oerebLader.scripts.s23_import_sizoplan.run(config)
oerebLader.scripts.s24_import_transfer_xtf.run(config)
oerebLader.scripts.s37_qa_sizoplan.run(config)
oerebLader.scripts.s38_qa_transfer.run(config)
oerebLader.scripts.s12_finish.run(config)

print("Workflow fertig!")