# -*- coding: utf-8 -*-
from odoo import fields, models


class UomUom(models.Model):
    _inherit = 'uom.uom'


    l10n_xma_uomcode = fields.Many2one(
        'l10n_xma.uomcode',
        string="Código unidad de medida"
    )

    l10n_xma_uomcode_id = fields.Many2one(
        'l10n_xma.uomcode',
        string="Código unidad de medida"
    )