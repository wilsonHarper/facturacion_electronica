# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit="product.template"


    l10n_xma_productcode_id = fields.Many2one(
        'l10n_xma.productcode',
        string="Código del SAT"
    )

    # br
    l10n_xma_cfop_id = fields.Many2one(
        string='Código Fiscal de Operações e Prestações',
        comodel_name='l10n_xma.cfop',
    )
    l10n_xma_product_type_id = fields.Many2one(
        string='Tipo de producto',
        comodel_name='l10n_xma.product_type',
    )
    l10n_xma_service_type_id = fields.Many2one(
        string='Tipo de servicio',
        comodel_name='l10n_xma.product_type',
    )


    l10n_xma_is_hazaudous_material = fields.Selection(
        [('si', "Si"),("no", "No")],
        string="Es Material Peligroso",
        related="l10n_xma_productcode_id.is_hazaudous_material"
    )
    l10n_xma_hazaudous_material_id = fields.Many2one(
        'l10n_xma.hazardous.material',
        string="Material Peligroso"
    )

    
    l10n_xma_need_retention = fields.Boolean(
        string='Necesita retención',
    )
    
