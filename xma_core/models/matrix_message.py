from odoo.models import Model
from odoo.fields import Char, Boolean


class MatrixMessage(Model):
    _name = "matrix.message"

    # Primary key
    message_id = Char(string="Message ID", required=True, index=True)

    processed = Boolean(string="Processed", default=False, help="True if the message has been processed")
    error = Boolean(string="Error", default=False, help="True if an error occurred while processing the message")
