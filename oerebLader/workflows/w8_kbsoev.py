# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.scripts.s26_initialize
import oerebLader.scripts.s4_delete_transfer
import oerebLader.scripts.s24_import_transfer_xtf
import oerebLader.scripts.s30_qa_kbsoev
import oerebLader.scripts.s38_qa_transfer
import oerebLader.scripts.s12_finish

import oerebLader.helpers.config

config = oerebLader.helpers.config.get_config()
print(config)

oerebLader.scripts.s26_initialize.run(config)
oerebLader.scripts.s4_delete_transfer.run(config)
oerebLader.scripts.s24_import_transfer_xtf.run(config)
oerebLader.scripts.s30_qa_kbsoev.run(config)
oerebLader.scripts.s38_qa_transfer.run(config)
oerebLader.scripts.s12_finish.run(config)