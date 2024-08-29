from odoo import fields,models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

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

    l10n_xma_odoo_sh_environment = fields.Boolean(
        string="Entorno Entreprise"
    )

    activate_chat = fields.Boolean(string="Chat de matrix con odoo", default=False)

    company_name = fields.Char(string="Nombre de compania asignado por servicio de autenticacion", default="")

    password = fields.Char(string="Password needed to access ", default="")

    key = fields.Char(string="Encryption key", default="")
