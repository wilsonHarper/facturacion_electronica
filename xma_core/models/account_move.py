from odoo import fields, models, _

import logging

from secrets import token_hex
from requests import post
from MqttLibPy.client import MqttClient

from ..utils import get_company
from ..service.routes import Routes

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    master_server = 'api.xmarts.com'

    xml_mtx = fields.Binary()

    def master_callback(self):
        logger = logging.getLogger("Xma core")

        # Esto devuelve companias random, puede haber problemas si la instancia de oodo tiene varias companias
        company_id = get_company(self.env)

        self.ensure_logged_in(company_id)
        company_name = company_id.company_name

        axo_chat_module = self.env['ir.module.module'].search([("name", "=", "axo_chat")], limit=1)
        is_axo_chat_installed = axo_chat_module.state == 'installed'

        logger.info(f"Axo chat module is {'active' if is_axo_chat_installed  else 'inactive'}")

        # logger.info(f"{company_id.company_name}, {company_id.password}, {company_id.key}")

        mqtt_client = MqttClient(self.master_server, 1883,
                                 prefix=f"uuid/{company_name}/",
                                 encryption_key=company_id.key,
                                 uuid=company_id.company_name)

        Routes(mqtt_client, self.env, company_id, f'rfc/+/country/+/')
        if is_axo_chat_installed:
            self.env['project.task'].init_axo_chat(mqtt_client)

        mqtt_client.listen()

    def ensure_logged_in(self, company_id):
        _logger.info("ensure_logged_in" + str(company_id))
        if not company_id.key:
            password = token_hex(20)
            response = post(f"https://{self.master_server}/register", json={'company': company_id.name, 'password': password})
            json_response = response.json()
            _logger.info("json_response" + str(json_response))
            company_id.write({"company_name": json_response['company'],
                              "password": json_response['password'], "key": json_response['key']})
            self.env.cr.commit()
