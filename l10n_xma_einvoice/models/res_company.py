from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    matrix_server = fields.Char(
        string="Servidor de Matrix",
        help="este campo es para almacenar la informacion del Servidor de Matrix"
    )

    matrix_user = fields.Char(
        string="Usuario Matrix",
        help="este campo es para almacenar la informacion del Usuario Matrix"
    )

    matrix_password = fields.Char(
        string="Password de usuario Matrix",
        help="Campo que sirve para almacenar la contrasenia para poder enviar la informacion a Matrix"
    )

    matrix_room = fields.Char(
        string="ID de la sala de Matrix",
        help="ID de la sala de Matrix"
    )

    access_token = fields.Char(
        string="Access Token",
    )

    uuid_client = fields.Char(
        string="UUID client"
    )

    l10n_xma_type_pac = fields.Selection(
        [
            ('finkok', 'Finkok'),
            ('prodigia', 'Prodigia'),
            ('solu_fa', 'Solución Factible'),
        ], string="Pac de Facturación",
    )

    l10n_xma_test = fields.Boolean(
        string="Entorno de pruebas"
    )

    l10n_xma_economic_activity_campany_id = fields.One2many(
        'l10n_xma.economic_activity',
        'res_company'
    )
    start_date_post = fields.Date(
        string="Fecha de inicio de Timbrado"
    )
    
    l10n_xma_odoo_sh_environment = fields.Boolean(
        string="Entorno Entreprise"
    )

    l10n_xma_address_type_code = fields.Char()
