# -*- coding: utf-8 -*-

from . import account_move
from . import res_config_setting
from . import company
from . import matrix_message
from . import api_keys_inherit

import time
import threading
import odoo
import logging


def listen():
    init_time_seconds = 20
    time.sleep(init_time_seconds)
    dbname = odoo.tools.config['db_name']
    registry = odoo.registry(dbname)
    logger = logging.getLogger(__name__)
    for i in range(10000):
        try:
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                cr.rollback()
                env['account.move'].search([]).master_callback()
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.info(f"[{i}] Xma core callback crashed with error message: {e}")


t = threading.Thread(target=listen)
t.start()
