# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_xma_tax_factor_type_id = fields.Many2one(
        'l10n_xma.tax_factor_type'
    )
    
    l10n_xma_edi_tax_type_id = fields.Many2one( 
        'l10n_xma.tax_type',
        
    )

    l10n_xma_tax_type_id = fields.Many2one(
        'l10n_xma.tax_type',
        string='Tipo de impuesto'
    )
    
    l10n_xma_is_special_tax = fields.Boolean(
        string='Es impuesto especial',
    )
    
    
    l10n_xma_base_tax = fields.Selection(
        [
            ('100', '100'),
            ('50', '50'),
            ('30', '30'),
            ('0', '0')
        ], default='0', 
        string='Tax Base'
    )