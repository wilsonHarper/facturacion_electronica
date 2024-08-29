from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit="account.move.line"    

    l10n_xma_tax_type_id = fields.Many2one(
        'l10n_xma.tax_type', string="Motivo de afectación"
    )
    l10n_xma_tax_situation_id = fields.Many2one(
        'l10n_xma.tax_situation', string="Situación tributaria"
    )
    l10n_xma_economic_activity_id = fields.Many2one(
        'l10n_xma.economic_activity', string="Actividad económina"
    )