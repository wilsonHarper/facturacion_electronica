# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit="product.product"


    l10n_xma_productcode_id = fields.Many2one(
        'l10n_xma.productcode',
        string="Código del SAT",
        related="product_tmpl_id.l10n_xma_productcode_id",
        readonly=False
    )

    l10n_xma_detraction_id = fields.Many2one(
        'l10n_xma.detraction',
    )

    l10n_xma_detraction_porcent = fields.Integer(related="l10n_xma_detraction_id.porcent")


    l10n_xma_origin_prod = fields.Many2one(
        'l10n_xma.origin_operation'
    )

    # br
    l10n_xma_cfop_id = fields.Many2one(
        string='Código Fiscal de Operações e Prestações',
        related="product_tmpl_id.l10n_xma_cfop_id"
    )

    l10n_xma_product_type_id = fields.Many2one(
        string='Tipo de producto',
        related="product_tmpl_id.l10n_xma_product_type_id"
    )
    l10n_xma_service_type_id = fields.Many2one(
        string='Tipo de servicio',
        related="product_tmpl_id.l10n_xma_service_type_id"
    )

    l10n_xma_is_hazaudous_material = fields.Selection(
        [('si', "Si"),("no", "No")],
        string="Es Material Peligroso",
        related='product_tmpl_id.l10n_xma_is_hazaudous_material'
    )
    l10n_xma_hazaudous_material_id = fields.Many2one(
        'l10n_xma.hazardous.material',
        string="Material Peligroso",
        related='product_tmpl_id.l10n_xma_hazaudous_material_id',
        readonly=False
    )
    l10n_xma_need_retention = fields.Boolean(
        string='Necesita retención',
        related='product_tmpl_id.l10n_xma_need_retention',
        readonly=False
    )