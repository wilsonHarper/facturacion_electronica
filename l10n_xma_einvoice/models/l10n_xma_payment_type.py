# -*- coding: utf-8 -*-
from odoo import fields, models

class l10nxmapaymenttype(models.Model):
    _name = "l10n_xma.payment_type"
    
    code = fields.Char()
    name = fields.Char()
    comments = fields.Text()

    def _get_name(self):
        name = super(l10nxmapaymenttype, self)._get_name()
        name = str('[' + self.code + ']' + self.name)
        return name