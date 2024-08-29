# -*- coding: utf-8 -*-
from odoo import fields, models



class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_xma_taxpayer_type_id = fields.Many2one(
        'l10n_xma.taxpayer_type',
        string='Taxpayer Type'
    )    
    
   
    commercial_name = fields.Char()
    
    external_number = fields.Char()
    
    internal_number = fields.Char()
    
    city_id = fields.Many2one('res.city')
    
    control_digit = fields.Char()
    
    municipality_id = fields.Many2one('l10n_xma.municipality', string="Municipio")
    
    is_taxpayer = fields.Boolean()
    
    customer_operation_type = fields.Selection([ ('1', 'Type 1'),
                                                ('2', 'Type 2'),
                                                ('3', 'Type 2'),
                                                ('4', 'Type 2'),],
                                               'Type')
    
    # Fields Paraguay invoices
    
    l10n_xma_external_number = fields.Char()
    
    l10n_xma_internal_number = fields.Char()
    
    l10n_xma_city_id = fields.Many2one(
        'res.city',string="Ciudad"
    )#fields.Many2one('res.city')
    
    l10n_xma_control_digit = fields.Char()
    
    l10n_xma_municipality_id = fields.Many2one(
        'l10n_xma.municipality', string='Municipio'
    )
    
    l10n_xma_is_taxpayer = fields.Boolean()
    
    l10n_xma_customer_operation_type = fields.Selection([ ('1', 'B2B'),
                                                ('2', 'B2C'),
                                                ('3', 'B2G'),
                                                ('4', 'B2F'),])
    # Fields Paraguay invoices 
   
    # Campo para los pagos MX

    l10n_xma_no_tax_breakdown = fields.Boolean(
        string="No Tax Breakdown",
        help="Includes taxes in the price and does not add tax information to the CFDI. Particularly in handy for IEPS. ")
    
    l10n_xma_ubigeo_code = fields.Char()


    # Fields Brasil invoices 

    l10n_xma_ie_indicator = fields.Selection([ ('1', '1-Contribuinte ICMS (informar a IE do destinatário)'),
                                                ('2', '2-Contribuinte isento de Inscrição no cadastro de Contribuintes do ICMS.'),
                                                ('3', '9-Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes do ICMS'),])


    
    l10n_xma_suframa_code = fields.Char(
        string='Suframa',
    )

    
    l10n_xma_is_principal_contact = fields.Boolean(
        string='Es el contacto principal',
    )

    
    l10n_xma_default_document_id = fields.Many2one(
        string='Tipo de documento',
        comodel_name='l10n_latam.document.type',
    )
    
    