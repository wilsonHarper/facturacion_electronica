import zipfile

from odoo import fields, models

from io import BytesIO
from os.path import dirname

from ..utils import get_company

class ResConfigSettingsIapFirebase(models.TransientModel):
    _inherit = 'res.config.settings'

    matrix_server = fields.Char(
        string="Servidor",
        help="este campo es para almacenar la informacion del Servidor",
        related="company_id.matrix_server",
        readonly=False
    )

    matrix_user = fields.Char(
        string="Usuario",
        help="este campo es para almacenar la informacion del Usuario",
        related="company_id.matrix_user",
        readonly=False
    )

    matrix_password = fields.Char(
        string="Password de usuario",
        help="Campo que sirve para almacenar la contrasenia para poder enviar la informacion",
        related="company_id.matrix_password",
        readonly=False
    )

    matrix_room = fields.Char(
        string="ID de la sala",
        help="ID de la sala de",
        related="company_id.matrix_room",
        readonly=False
    )

    access_token = fields.Char(
        string="Access Token",
    )

    uuid_client = fields.Char(
        related='company_id.uuid_client',
        readonly=False
    )

    l10n_xma_type_pac = fields.Selection(
        [
            ('finkok', 'Finkok'),
            ('prodigia', 'Prodigia'),
            ('solu_fa', 'Solución Factible'),
        ], string="Pac de Facturación",
        related="company_id.l10n_xma_type_pac",
        readonly=False
    )
    
    l10n_xma_test = fields.Boolean(
        string="Entorno de pruebas",
        related="company_id.l10n_xma_test",
    )

    l10n_xma_odoo_sh_environment = fields.Boolean(
        string="Entorno de pruebas",
        related="company_id.l10n_xma_odoo_sh_environment",
        readonly=False
    )


    activate_chat = fields.Boolean(related="company_id.activate_chat", string="Chat de matrix con odoo", readonly=False)

    def generate_zip(self, files):
        mem_zip = BytesIO()

        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f[0], f[1])

        return mem_zip.getvalue()

    def main(self):
        file_names = ["certificado.cer", "certificado.key", "password.txt"]
        files = []

        for file_name in file_names:
            path = f"{dirname(dirname(__file__))}/test/{file_name}"
            file = open(path, "rb")  # Reemplazar por bytes de la base de datos
            _bytes = file.read()
            file.close()
            files.append((file_name, _bytes))

        full_zip_in_memory = self.generate_zip(files)
        self.send_file(full_zip_in_memory)

    def send_file(self, file: bytes):
        company = get_company(self.env)

        client = AsyncMatrix(is_bot=True, env=self.env)
        client.send_file_message_from_bytes(BytesIO(file), company.matrix_room, 'application/zip', "test_file.zip")
        client.execute(1)
