# -*- coding: utf-8 -*-
from odoo import fields, models

class LatamDocument(models.Model):
    _inherit = "l10n_latam.document.type"
    
    l10n_xma_authorization_code = fields.Char()
    l10n_xma_branch = fields.Char()
    l10n_xma_dispatch_point = fields.Char()
    l10n_xma_sequence_start = fields.Integer()
    l10n_xma_sequence_end = fields.Integer()
    l10n_xma_date_start = fields.Date()
    l10n_xma_date_end = fields.Date()
    internal_type = fields.Selection(
        selection_add=[
            ('receipt_invoice', 'Recibo Electronico'),
        ]
    )
