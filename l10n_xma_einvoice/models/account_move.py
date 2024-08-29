# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import json
from lxml.objectify import fromstring
import base64
from datetime import datetime
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError
import time
import re
from random import choice, randint
from xml.etree import ElementTree as ET
from io import BytesIO, StringIO
from xml.dom import minidom
import qrcode
from num2words import num2words
from MqttLibPy.client import MqttClient
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    country_id = fields.Many2one(
        'res.country',
        related="company_id.country_id",
    )
    # -- Fields for MX Invoicing --
    l10n_xma_invoice_cfdi = fields.Binary(
        string = 'Cfdi content', copy = False, readonly = True,
        help = 'The cfdi xml content encoded in base64.')
    
    l10n_xma_invoice_cfdi_name = fields.Char(
        string = 'CFDI name',
        copy = False,
        readonly = True,
        help = 'The attachment name of the CFDI.')

    l10n_xma_payment_form = fields.Many2one(
        'xma_payment.form',
        string="Forma de pago"
    )

    l10n_xma_timbre = fields.Boolean(default=False, copy=False)

    l10n_xma_cadena_original = fields.Char(string="Cadena Original", copy=False)

    l10n_xma_uuid_invoice = fields.Char(string="Folio Fiscal" , copy=False)

    l10n_xma_post_time = fields.Datetime(string="Fecha de Timbrado", copy=False)

    l10n_xma_cfdi_request = fields.Selection(
        selection=[
            ('on_invoice', "On Invoice"),
            ('on_refund', "On Credit Note"),
            ('on_payment', "On Payment"),
        ],
        string="Request a CFDI", store=True,
        compute='_compute_l10n_xma_cfdi_request',
        help="Flag indicating a CFDI should be generated for this journal entry.")

    l10n_xma_origin = fields.Char(
        string='CFDI Origin',
        copy=False,
        help="In some cases like payments, credit notes, debit notes, invoices re-signed or invoices that are redone "
             "due to payment in advance will need this field filled, the format is:\n"
             "Origin Type|UUID1, UUID2, ...., UUIDn.\n"
             "Where the origin type could be:\n"
             "- 01: Nota de crédito\n"
             "- 02: Nota de débito de los documentos relacionados\n"
             "- 03: Devolución de mercancía sobre facturas o traslados previos\n"
             "- 04: Sustitución de los CFDI previos\n"
             "- 05: Traslados de mercancias facturados previamente\n"
             "- 06: Factura generada por los traslados previos\n"
             "- 07: CFDI por aplicación de anticipo")

    
    # -- Fields for MX Invoicing --

    l10n_xma_test_bolean = fields.Boolean(
        string="Entorno de prueba", related="company_id.l10n_xma_test"
    )

    l10n_xma_use_document_id = fields.Many2one(
        'l10n_xma.use.document',
        string='Use Document'
    )    
    l10n_xma_payment_type_id = fields.Many2one(
        'l10n_xma.payment_type',
        string='EDI Payment Type',
        # compute="get_ppd_or_pue_mx",
    )

    
    l10n_xma_totalpages = fields.Integer(
        string='Total de paginas',
    )

    

    l10n_xma_payment_form_ids = fields.One2many(
        'xma_payment.form',
        'account_move_id'
    )
    

    
    @api.onchange('l10n_xma_document_type')
    def onchange_l10n_latam_document_type_id(self):
        self.l10n_latam_document_type_id = self.l10n_xma_document_type


    # @api.depends('invoice_payment_term_id')
    # def get_ppd_or_pue_mx(self):
    #     if self.invoice_payment_term_id:
    #         metodo = self._einvoice_edi_get_payment_policy()
    #         rec = self.env['l10n_xma.payment_type'].search([
    #             ('code', '=', metodo)
    #         ])
    #         self.l10n_xma_payment_type_id = rec.id
    #     else:
    #        self.l10n_xma_payment_type_id = False 


    l10n_xma_edi_legal_status_id = fields.Many2one(
        'l10n_xma.edi.legal.status',
        string='EDI Legal Status'
    )
    l10n_xma_edi_related = fields.Char(
        string='EDI Related'
    )
    
    l10n_xma_origin_operation_id = fields.Many2one(
        'l10n_xma.origin_operation',
        string='Use Document'
    )    
    
    l10n_xma_issuance_type_id = fields.Many2one(
        'l10n_xma.issuance_type',
        string='Use Document'
    )    
    
    l10n_xma_edi_einvoice  = fields.Char(readonly=True, copy=False)

    l10n_xma_document_type = fields.Many2one(
        'l10n_latam.document.type', string="Tipo de Documento"
    )

    ramdom_code = fields.Char(readonly=True, copy=False)
    l10n_xma_cdc_code = fields.Char("Código de control (CDC)")


    l10n_xma_document_id = fields.Char(
        string='ID del documento'
    )
    
    l10n_xma_date_post = fields.Datetime(
        string='Fecha de timbrado'
    )
    
    l10n_xma_security_code = fields.Char(
        string='Código de seguridad'
    )
    
    l10n_xma_payment_form_id = fields.Many2one(
        'xma_payment.form',
        string='Forma de pago'
    ) 
    is_einvoice_send = fields.Boolean(
        string="Timbrado",
        copy=False
    )
    l10n_xma_document_type_rel = fields.Char(
        string="Tipo de documento relacionado",
        related='l10n_xma_document_type.code'
    )

    l10n_xma_xml_ar = fields.Binary(
        string = 'Invoice Xml', copy = False, readonly = False,
        help = 'The xml content encoded in base64.')
    
    l10n_xma_xml_name = fields.Char(
        string = 'Xml name',
        copy = False,
        readonly = True)
    
    l10n_xma_tipo_doc_asociado = fields.Selection(
        [('0', ''),
            ('1', 'Electrónico'),
            ('2','Impreso'),
            ('3', 'Constancia Electrónica')], default="0",
         string="Tipo de documento asociado"
    )

    l10n_xma_cdc_asociado = fields.Char(
        string="CDC Asociado", copy=False
    )

    l10n_xma_number_timbrado_asociado = fields.Char(
        string="Numero de Timbrado asociado",
    )

    l10n_xma_cod_state_asociado = fields.Char(
        string="Codigo de establecimiento asociado",
    )

    l10n_xma_point_exp_asociado = fields.Char(
        string="Punto de expedicion asociado",
    )

    l10n_xma_document_number_asociado = fields.Char(
        string="Numero del Documento"
    )

    l10n_document_type_asociado = fields.Selection(
        [('1','Factura'),
         ('2','Nota de crédito'),
         ('3', 'Nota de débito'),
         ('4', 'Nota de remisión'),
         ('5', 'Comprobante de retención')
        ],default="1", string="Tipo de documento"
    )

    l10n_xma_date_document_emision = fields.Date(
        string="Fecha de emision del Documento",
        copy=False,
    )

    l10n_mx_emi_motive = fields.Selection(
        [('1', 'Devolución y Ajuste de precios'),
         ('2', 'Devolución'),
         ('3', 'Descuento'),
         ('4', 'Bonificación'),
         ('5', 'Crédito incobrable'),
         ('6', 'Recupero de costo'),
         ('7', 'Recupero de gasto'),
         ('8', 'Ajuste de precio'),
        ],default="1", string="Motivo de Emision"
    )

    l10n_xma_qr = fields.Binary(
        string="QR",
    )

    l10n_xma_sif_status = fields.Selection(
        [('fail', 'Rechazado'),
         ('sign', 'Firmado'),
         ('auto', 'Autorizado')],
         string="Estado del Documento ante el Gobierno"
    )

    l10n_pe_edi_is_required = fields.Char()

    l10n_xma_odoo_sh_environment = fields.Boolean(
        string="Entorno de prueba", related="company_id.l10n_xma_odoo_sh_environment"
    )

    @api.onchange('l10n_xma_date_post')
    def onchange_l10n_xma_date_post(self):
        if self.l10n_xma_date_post:
            self.invoice_date = self.l10n_xma_date_post.date()
            

    def generate_qr(self, url):
        qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=20,border=4,)
        qr.add_data(url) #you can put here any attribute SKU in my case
        qr.make(fit=True)
        img = qr.make_image()
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()





    def generate_cdc(self):
        newNumCDC = ''
        for i in range(0, len(self.l10n_xma_uuid_invoice), 4):
            newNumCDC += self.l10n_xma_uuid_invoice[i:i + 4] + " "

        return newNumCDC
            # -- Metodos  Localizacion MX --
    # def _get_l10n_mx_edi_signed_edi_document(self):
    #     return self.l10n_xma_invoice_cfdi

    def l10n_xma_amount_to_text(self):
        self.ensure_one()
        currency = self.currency_id.name.upper()
        currency_type = 'M.N' if currency == 'MXN' else 'M.E.'
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.currency_id.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount_i).upper()
        invoice_words = '%(words)s %(amount_d)02d/100 %(curr_t)s' % dict(
            words=words, amount_d=amount_d, curr_t=currency_type)
        return invoice_words

    @api.model
    def edi_get_xml_etree(self, cfdi=None):
        self.ensure_one()
        if cfdi is None and self.l10n_xma_invoice_cfdi:
            cfdi = base64.decodebytes(self.l10n_xma_invoice_cfdi)
        return fromstring(cfdi) if cfdi else None

    @api.model
    def edi_get_tfd_etree(self, cfdi):
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = 'tfd:TimbreFiscalDigital[1]'
        namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node[0] if node else None
    
    @api.model
    def edi_get_xml_etree_py(self, py_xml=None):
        for rec in self:
            if rec.l10n_xma_xml_ar:
                stream = BytesIO(base64.b64decode(rec.l10n_xma_xml_ar))
                doc = minidom.parse(stream)
                Test = doc.getElementsByTagName("dCarQR")[0]
                print(Test.firstChild.data)
                return Test.firstChild.data

    def get_company(self):
        company_id = self.env['res.company'].sudo().search([("company_name", "!=", "")], limit=1)
        if not company_id:
            company_id = self.env['res.company'].search([], limit=1)

        return company_id

    def send_to_matrix_json_mx(self):
        xml_json_mx = self.generate_json_l10n_mx()
        xml_json = {"MX": xml_json_mx}
        company = self.get_company()
        uuid = company.company_name
        rfc = self.company_id.partner_id.vat
        country = self.company_id.partner_id.country_id.code.lower()
        xml_json = {"from":uuid, "data":xml_json}
        mqtt_client = MqttClient("api.xmarts.com", 1883, prefix=f"uuid/{uuid}/rfc/{rfc}/country/{country}/", encryption_key=company.key)
        # xml_json = json.dumps(xml_json)
        print(xml_json)
        mqtt_client.send_message_serialized(
            [xml_json],
            f"uuid/{uuid}/rfc/{rfc}/country/{country}/stamp", 
            valid_json=True, 
            secure=True
        )

        time.sleep(1)
        self.refresh_account_move_xma()


    def refresh_account_move_xma(self):
        print("REFRESH ACCOUNT")
        return {
            'name': _("Facturacion"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.id)],
            'target': 'current',
            'res_id': self.id,
        }
    

    @api.model
    def _l10n_mx_edi_is_managing_invoice_negative_lines_allowed(self):
        """ Negative lines are not allowed by the Mexican government making some features unavailable like sale_coupon
        or global discounts. This method allows odoo to distribute the negative discount lines to each others making
        such features available even for Mexican people.

        :return: True if odoo needs to distribute the negative discount lines, False otherwise.
        """
        param_name = 'l10n_mx_edi.manage_invoice_negative_lines'
        return bool(self.env['ir.config_parameter'].sudo().get_param(param_name))

    @api.depends('move_type', 'company_id', 'state')
    def _compute_l10n_xma_cfdi_request(self):
        
        for move in self:
            try:
                if move.country_code != 'MX':
                    move.l10n_xma_cfdi_request = False
                elif move.move_type == 'out_invoice':
                    move.l10n_xma_cfdi_request = 'on_invoice'
                elif move.move_type == 'out_refund':
                    move.l10n_xma_cfdi_request = 'on_refund'
                elif (move.payment_id and move.payment_id.payment_type == 'inbound' and
                    'PPD' in move._get_reconciled_invoices().mapped('l10n_xma_payment_type_id')):
                    move.l10n_xma_cfdi_request = 'on_payment'
                elif move.statement_line_id:
                    move.l10n_xma_cfdi_request = 'on_payment'
                else:
                    move.l10n_xma_cfdi_request = False
            except Exception as e:
                _logger.info("e")

    def _get_l10n_mx_edi_issued_address(self):
        self.ensure_one()
        return self.company_id.partner_id.commercial_partner_id

    @api.model
    def _l10n_mx_edi_read_cfdi_origin(self, cfdi_origin):
        splitted = cfdi_origin.split('|')
        if len(splitted) != 2:
            return False

        try:
            code = int(splitted[0])
        except ValueError:
            return False

        if code < 1 or code > 7:
            return False
        return splitted[0], [uuid.strip() for uuid in splitted[1].split(',')]

    def _get_xma_issued_address(self):
        self.ensure_one()
        return self.company_id.partner_id.commercial_partner_id

    def _l10n_xma_get_tax_objected(self):
        """Used to determine the IEPS tax breakdown in CFDI
             01 - Used by foreign partners not subject to tax
             02 - Default for MX partners. Splits IEPS taxes
             03 - Special override when IEPS split / Taxes are not required"""
        self.ensure_one()
        customer = self.partner_id if self.partner_id.type == 'invoice' else self.partner_id.commercial_partner_id
        if customer.l10n_xma_no_tax_breakdown:
            return '03'
        
        elif (self.move_type in self.get_invoice_types() and not self.invoice_line_ids.tax_ids) or \
             (self.move_type == 'entry' and not self._get_reconciled_invoices().invoice_line_ids.tax_ids):
            return '01'
        else:
            print('02')
            return '02'

    def _einvoice_edi_get_payment_policy(self):
        try:
            self.ensure_one()
            version = '4.0'
            term_ids = self.invoice_payment_term_id.line_ids
            if version == '3.2':
                if len(term_ids.ids) > 1:
                    return 'Pago en parcialidades'
                else:
                    return 'Pago en una sola exhibición'
            
            elif version == '4.0' and self.invoice_date_due and self.l10n_xma_date_post:

                if self.move_type == 'out_refund' and len(term_ids) == 1:
                    print('PUE')
                    return 'PUE'
                
                if self.invoice_date_due.month > self.l10n_xma_date_post.date().month or \
                self.invoice_date_due.year > self.l10n_xma_date_post.date().year or \
                len(term_ids) > 1:  # to be able to force PPD
                    print("PPD1-1-1--")
                    return 'PPD'
                print("PUE")
                return 'PUE'
            return ''
        except:
            pass

    def get_mx_current_datetime_mx(self):
        return fields.Datetime.context_timestamp(
            self.with_context(tz='America/Mexico_City'), self.l10n_xma_date_post)

    def get_mx_current_datetime_do(self):
        return fields.Datetime.context_timestamp(
            self.with_context(tz='America/Santo_Domingo'), self.l10n_xma_date_post)


    def get_mx_current_datetime(self):
        tz = self.env.user.tz or 'UTC'
        return fields.Datetime.context_timestamp(
            self.with_context(tz=tz), self.l10n_xma_date_post)
    
    __check_cfdi_partner_name_re = re.compile(u'''([A-Z]|[a-z]|[0-9]|.| |Ñ|ñ|!|"|%|&|'|´|-|:|;|>|=|<|@|_|,|\{|\}|`|~|á|é|í|ó|ú|Á|É|Í|Ó|Ú|ü|Ü)''')

    @staticmethod
    def _get_string_cfdi_partner_name(text, size=100):
        """Replace from text received the characters that are not found in the
        regex. This regex is taken from SAT documentation
        https://goo.gl/C9sKH6
        text: Text to remove extra characters
        size: Cut the string in size len
        Ex. 'Product ABC (small size)' - 'Product ABC small size'
        This version adds the dot symbol as an allowed character.
        """
        if not text:
            return None
        for char in AccountMove.__check_cfdi_partner_name_re.sub('', text):
            text = text.replace(char, ' ')
        return text.strip()[:size]
    
    def generate_json_l10n_mx(self):
        if self.invoice_payment_term_id:
            metodo = self._einvoice_edi_get_payment_policy()
            rec = self.env['l10n_xma.payment_type'].search([
                ('code', '=', metodo)
            ])
            self.l10n_xma_payment_type_id = rec.id
        def subtotal_wo_discount(l): return float_round(
            l.price_subtotal / (1 - l.discount/100) if l.discount != 100 else
            l.price_unit * l.quantity, int(2))
        def tax_name(t): return {
            'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(t, False)
        
        time_invoice = self.get_mx_current_datetime_mx()
        conceptos = []
        for items in self.invoice_line_ids:
            if items.product_id:
                traslados1 = []
                retenciones1 = []
                obje_imp = 0
                if items.tax_ids:
                    for taxes in items.tax_ids:
                        if taxes.amount >= 0:
                            obje_imp+=1
                            print("items.tax_base_amount * (taxes.amount / 100)", items.tax_base_amount * (taxes.amount / 100))
                            print('items.tax_base_amount', items.tax_base_amount, 'taxes.amount', taxes.amount)
                            traslados1.append({
                                'cfdi:Traslado': {
                                    'Base': items.price_subtotal,
                                    'Impuesto': taxes.l10n_xma_tax_type_id.code, 
                                    'TipoFactor': taxes.l10n_xma_tax_factor_type_id.name, 
                                    'TasaOCuota': '%.6f' % abs(taxes.amount if taxes.amount_type == 'fixed' else (taxes.amount / 100.0)), 
                                    'Importe': round(items.price_subtotal * (taxes.amount / 100), 2)
                                }
                            })
                        else:
                            obje_imp+=1
                            print("items.tax_base_amount * (taxes.amount / 100)", items.tax_base_amount * (taxes.amount / 100))
                            print('items.tax_base_amount', items.tax_base_amount, 'taxes.amount', taxes.amount)
                            retenciones1.append({
                                'cfdi:Retencion': {
                                    'Base': items.price_subtotal,
                                    'Impuesto': taxes.l10n_xma_tax_type_id.code, 
                                    'TipoFactor': taxes.l10n_xma_tax_factor_type_id.name, 
                                    'TasaOCuota': '%.6f' % abs(taxes.amount if taxes.amount_type == 'fixed' else (taxes.amount / 100.0)), 
                                    'Importe': round(items.price_subtotal * (taxes.amount / 100), 2) * -1
                                }
                            })
                print(':::::::::::::::::::::::traslados:::::::::::::::::::::::::', traslados1)
                conceptos.append({
                    'cfdi:Concepto':{
                        'ClaveProdServ':items.product_id.l10n_xma_productcode_id.code,
                        'NoIdentificacion': items.product_id.default_code or '',
                        'Cantidad': '%.6f' % items.quantity,
                        'ClaveUnidad': items.product_uom_id.l10n_xma_uomcode.code,
                        'Unidad': items.product_uom_id.name,
                        'Descripcion': items.name.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'),
                        'ValorUnitario': '%.*f' % (self.currency_id.decimal_places, subtotal_wo_discount(items)/items.quantity) if items.quantity else 0.0,
                        'Importe': '%.*f' % (self.currency_id.decimal_places, subtotal_wo_discount(items)),
                        'ObjetoImp': '02' if obje_imp > 0 else '01',
                        'Descuento': ('%.*f' % (self.currency_id.decimal_places, subtotal_wo_discount(items) - items.price_subtotal)),
                        'cfdi:Impuestos': {
                            'cfdi:Traslados': traslados1 if traslados1 else [],
                            'cfdi:Retenciones': retenciones1 if retenciones1 else []
                        }
                    },
                })
        # traslados = []

        # for line in self.invoice_line_ids:
        #     for taxes in line.tax_ids:
        #         traslados.append({
        #             'cfdi:Traslado': {
        #                 'Importe': self.amount_total, 
        #                 'Impuesto': taxes.l10n_xma_tax_type_id.code,
        #                 'TipoFactor': taxes.l10n_xma_tax_factor_type_id.name,
        #                 'TasaOCuota': self.amount_total * (taxes.amount / 100)
        #             }
        #         })
        total_withhold = 0
        withhold_count = 0
        total_transferred = 0
        transferred_count = 0
        name_transferred = ""
        name_withhold = ""
        type_transferred = ""
        taxes_lines = []

        transferred_taxes = []

        withhold_taxes = []

        for line in self.invoice_line_ids.filtered('price_subtotal'):
            price = line.price_unit * \
                (1.0 - (line.discount or 0.0) / 100.0)
            tax_line = {tax['id']: tax for tax in line.tax_ids.compute_all(
                price, line.currency_id, line.quantity, line.product_id, line.partner_id, self.move_type in ('in_refund', 'out_refund'))['taxes']}
            for tax in line.tax_ids.filtered(lambda r: r.l10n_xma_tax_factor_type_id.name != 'Exento'):
                tax_dict = tax_line.get(tax.id, {})
                tasa = '%.6f' % abs(
                            tax.amount if tax.amount_type == 'fixed' else (tax.amount / 100.0))
                amount = round(abs(tax_dict.get(
                    'amount', tax.amount / 100 * float("%.2f" % line.price_subtotal))), 2)
                basee = round(float(amount) / float(tasa) if tax.amount_type == 'fixed' else tax_dict.get('base', line.price_subtotal), line.currency_id.decimal_places)
                if tax.amount >= 0:
                    total_transferred = round((total_transferred + amount), 2)
                    name_transferred = tax.l10n_xma_tax_type_id.code
                    print("------------------------------", name_transferred)
                    type_transferred = tax.l10n_xma_tax_factor_type_id.name

                    exist = False
                    print("LISTAAAAAA: ", transferred_taxes)
                    for tt in transferred_taxes:
                        if tax.id == tt['cfdi:Traslado']['id']:
                            exist = True
                            tt['cfdi:Traslado']['Importe'] += round(amount, 2)
                            tt['cfdi:Traslado']['Base'] += basee
                    if exist == False:
                        transferred_taxes.append({'cfdi:Traslado': {
                            'id': tax.id,
                            "Base": basee,
                            # "Base": '%.*f' % (line.currency_id.decimal_places, float(amount) / float(tasa) if tax.amount_type == 'fixed' else tax_dict.get('base', line.price_subtotal)),
                            'Importe': round(amount, 2),
                            'Impuesto': name_transferred,
                            'TipoFactor': type_transferred,
                            'TasaOCuota': '%.6f' % abs(tax.amount if tax.amount_type == 'fixed' else (tax.amount / 100.0))
                        }})
                        print("______________________________", transferred_taxes)
                else:
                    total_withhold += amount
                    name_withhold = tax_name(tax.mapped('invoice_repartition_line_ids.tag_ids')[0].name if tax.mapped(
                        'invoice_repartition_line_ids.tag_ids') else '')

                    exist = False
                    for wt in withhold_taxes:
                        if tax.id == wt['cfdi:Retencion']['id']:
                            exist = True
                            wt['cfdi:Retencion']['Importe'] += amount
                    if exist == False:
                        withhold_taxes.append({'cfdi:Retencion': {
                            'id': tax.id,
                            'Importe': round(amount, 2),
                            'Impuesto': tax.l10n_xma_tax_type_id.code
                        }})
        for tt in transferred_taxes:
            del tt['cfdi:Traslado']['id']
            tt['cfdi:Traslado']['Importe'] = round(tt['cfdi:Traslado']['Importe'], self.currency_id.decimal_places)
            tt['cfdi:Traslado']['Base'] = round(tt['cfdi:Traslado']['Base'], self.currency_id.decimal_places)
        for wt in withhold_taxes:
            del wt['cfdi:Retencion']['id']
            wt['cfdi:Retencion']['Importe'] = round(wt['cfdi:Retencion']['Importe'], self.currency_id.decimal_places)
        def get_discount(l, d): return (
                '%.*f' % (int(d), subtotal_wo_discount(l) - l.price_subtotal)) if l.discount else False
        total_discount = sum([float(get_discount(p, 2))
                                for p in self.invoice_line_ids])
        amount_untaxed = '%.*f' % (2, sum([subtotal_wo_discount(p)
                                               for p in self.invoice_line_ids]))
        
        cfdi_impuestos = {}
        # if total_transferred != 0 or total_withhold != 0:
        #     continue
        cfdi_impuestos = {
            'TotalImpuestosTrasladados': total_transferred if total_transferred > 0 else 0,
            'cfdi:Retenciones': withhold_taxes,
            'cfdi:Traslados': transferred_taxes
        }
        if total_withhold:
            cfdi_impuestos['TotalImpuestosRetenidos'] = total_withhold
        condiciones = str(self.invoice_payment_term_id.name).replace('|', ' ')
        document_type = 'ingreso' if self.move_type == 'out_invoice' else 'egreso'
        date = self.invoice_date or fields.Date.today()
        company_id = self.company_id
        ctx = dict(company_id=company_id.id, date=date)
        mxn = self.env.ref('base.MXN').with_context(ctx)
        invoice_currency = self.currency_id.with_context(ctx)
        print("amount_untaxed", amount_untaxed)
        print("total_discount", total_discount)
        print("total_transferred", total_transferred)
        print("total_withhold", total_withhold)
        descuento = float('%.*f' % (2, total_discount) if total_discount else 0)
        json_m = {
            "xsi:schemaLocation": "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/ComercioExterior11 http://www.sat.gob.mx/sitio_internet/cfd/ComercioExterior11/ComercioExterior11.xsd",
            "xmlns:cfdi": "http://www.sat.gob.mx/cfd/4" ,
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:cce11": "http://www.sat.gob.mx/ComercioExterior11",
            'Version': '4.0',
            'Fecha': time_invoice.strftime('%Y-%m-%dT%H:%M:%S'),
            'Folio': self.sequence_number,
            'Serie': self.sequence_prefix,
            'Sello': '',
            'FormaPago': self.l10n_xma_payment_form.code,
            'NoCertificado': '',
            'Certificado': '',
            'CondicionesDePago':condiciones.strip()[:1000] if self.invoice_payment_term_id else False,
            'SubTotal': '%0.*f' % (2,float(self.amount_untaxed + descuento)),
            'Descuento': '%.*f' % (2, total_discount) if total_discount else 0,
            'Moneda': self.currency_id.name,
            'TipoCambio':('%.6f' % (invoice_currency._convert(1, mxn, self.company_id, self.invoice_date or fields.Date.today(), round=False))) if self.currency_id.name != 'MXN' else {},
            'Total': '%0.*f' % (2, float(amount_untaxed) - float(float('%.*f' % (2, total_discount)) or 0) + (
                    float(total_transferred) or 0) - (float(total_withhold) or 0)),
            'TipoDeComprobante': document_type[0].upper(),
            'Exportacion': '01',
            'MetodoPago':  self.l10n_xma_payment_type_id.code,
            'LugarExpedicion': self.company_id.zip or  self.company_id.partner_id.zip,
            'cfdi:CfdiRelacionados': [], 
            'cfdi:Emisor': {
                'Rfc': self._get_string_cfdi_partner_name(self.company_id.vat.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'), 254),
                'Nombre': self._get_string_cfdi_partner_name(self.company_id.name.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'), 254),
                'RegimenFiscal':self.company_id.partner_id.l10n_xma_taxpayer_type_id.code
            },
            'cfdi:Receptor': {
                'Rfc': self._get_string_cfdi_partner_name(self.partner_id.vat.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'), 254),
                'Nombre': self._get_string_cfdi_partner_name(self.partner_id.name.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'), 254),
                'UsoCFDI': self.l10n_xma_use_document_id.code,
                'DomicilioFiscalReceptor':self.partner_id.zip,
                'RegimenFiscalReceptor': self.partner_id.l10n_xma_taxpayer_type_id.code
            },
            'cfdi:Conceptos': conceptos,
            'cfdi:Impuestos': cfdi_impuestos
        }

        json_complete = {
            "id":self.id,
            "uuid_client":self.company_id.uuid_client,
            "data":json_m,
            "rfc":self.company_id.vat,
            "prod": 'NO' if self.company_id.l10n_xma_test else 'SI',
            "type": 'F',
            "pac_invoice": self.company_id.l10n_xma_type_pac,
        }

        # json_complete = json.dumps(json_complete, default=str, separators=(',', ':'), ensure_ascii=True)

        # res = str(json_complete)
        # print(res)
        return json_complete


    def generate_json_l10n_do(self):
        for rec in self:
            time_invoice = self.get_mx_current_datetime_do()
            IndicadorBienoServicio = 0
            
            DatosItem = []
            line = 1
            MontoGravadoTotal = 0
            MontoGravadoI1 = 0
            ITBIS1 = 0
            TotalITBIS = 0
            MontoGravadoI2 = 0
            TotalITBIS2 = 0
            TotalITBIS1 = 0

            for ite in rec.line_ids:
                if ite.tax_tag_ids and ite.credit > 0:
                    for tag in ite.tax_tag_ids:
                        if tag.l10n_xma_tax_type_id.code in ['1','2','3']:                            
                            TotalITBIS +=  ite.credit
                        if tag.l10n_xma_tax_type_id.code in ['1']:
                            print("++++++++ lines.l10n_xma_tax_type_id.code in ['1']    ++++++++++")
                            MontoGravadoI1 += ite.credit
                            ITBIS1 += 1
                            TotalITBIS1 += ite.credit
                        
                        if tag.l10n_xma_tax_type_id.code in ['2']:
                            print("++++++++ lines.l10n_xma_tax_type_id.code in ['1']    ++++++++++")
                            MontoGravadoI2 += ite.credit
                            # TotalITBIS2 += ite.credit


            for lines in self.invoice_line_ids:                
                if ite.product_id.detailed_type == 'consu' or lines.product_id.detailed_type == 'product':
                    IndicadorBienoServicio = 1
                else:
                    IndicadorBienoServicio = 2
                descuento =  lines.quantity * lines.price_unit - lines.price_subtotal

                if descuento > 0:
                    DatosItem.append({
                        "Item": {
                                "NumeroLinea": line,
                                "IndicadorFacturacion": lines.l10n_xma_tax_type_id.code,
                                "NombreItem": lines.name,
                                "IndicadorBienoServicio": IndicadorBienoServicio,
                                "CantidadItem": lines.quantity,
                                "PrecioUnitarioItem": '%.2f' % float(lines.price_unit),
                                "DescuentoMonto": '%.2f' % float(descuento),                                
                                "TablaSubDescuento": {
                                    "SubDescuento": {
                                        "TipoSubDescuento": '$',
                                        # "SubDescuentoPorcentaje": ,
                                        "MontoSubDescuento": '%.2f' % float(descuento),
                                    }
                                },
                                "MontoItem": '%.2f' % float(lines.price_subtotal),
                            }
                    })
                if descuento == 0:
                    DatosItem.append({
                        "Item": {
                                "NumeroLinea": line,
                                "IndicadorFacturacion": lines.l10n_xma_tax_type_id.code,
                                "NombreItem": lines.name,
                                "IndicadorBienoServicio": IndicadorBienoServicio,
                                "CantidadItem": lines.quantity,
                                "PrecioUnitarioItem": '%.2f' % float(lines.price_unit),                                
                                "MontoItem": '%.2f' % float(lines.price_subtotal + descuento),                                
                            }
                    })
                line += 1

            print("Provincia", rec.company_id.partner_id.state_id.l10n_xma_statecode)
            print("CorreoEmisor", rec.company_id.email)
            json_m = {
                    "ECF": {
                        "Encabezado": {
                            "Version": "1.0",
                            "IdDoc": {
                                "TipoeCF": rec.l10n_latam_document_type_id.code,
                                "eNCF": "E310000000170",
                                "FechaVencimientoSecuencia": rec.l10n_latam_document_type_id.l10n_xma_date_end.strftime('%d-%m-%Y'),
                                "IndicadorMontoGravado": "0",
                                "TipoIngresos": rec.l10n_xma_use_document_id.code,
                                "TipoPago": rec.l10n_xma_payment_type_id.code,
                            },
                            "Emisor": {
                                "RNCEmisor": rec.company_id.vat,
                                "RazonSocialEmisor": rec.company_id.name,
                                "NombreComercial": rec.company_id.partner_id.commercial_partner_id.name,
                                "DireccionEmisor": rec.company_id.street,
                                "Municipio": rec.company_id.partner_id.l10n_xma_municipality_id.code,
                                "Provincia": rec.company_id.partner_id.state_id.l10n_xma_statecode,
                                "TablaTelefonoEmisor": {
                                    "TelefonoEmisor": rec.company_id.phone
                                },
                                "CorreoEmisor": rec.company_id.email,
                                "FechaEmision": rec.invoice_date.strftime('%d-%m-%Y'),
                            },
                            "Comprador": {
                                "RNCComprador": rec.partner_id.vat,
                                "RazonSocialComprador": rec.partner_id.name
                            },
                            "Totales": {
                                "MontoGravadoTotal": rec.amount_untaxed_signed,
                                "MontoGravadoI1": MontoGravadoI1 / .18,
                                "MontoGravadoI2": MontoGravadoI2 / .16,
                                "ITBIS1": '18' if MontoGravadoI1 > 0 else {},
                                "ITBIS2": '16' if MontoGravadoI2 > 0 else {},                                                          
                                "TotalITBIS": TotalITBIS,
                                "TotalITBIS1": MontoGravadoI1,
                                "TotalITBIS2": MontoGravadoI2,
                                "MontoTotal": rec.amount_total
                            }
                        },
                        "DetallesItems": DatosItem,
                        "FechaHoraFirma": time_invoice.strftime('%d-%m-%Y %H:%M:%S')
                }
            }
            print("json", json_m)
            json_complete = {
                "id":self.id,
                "uuid_client":self.company_id.uuid_client,
                "data":json_m,
                "rfc":self.company_id.vat,
                "prod": 'NO' if self.company_id.l10n_xma_test else 'SI',
                "type": 'FD',
                "pac_invoice": self.company_id.l10n_xma_type_pac,
                
            }

            # json_complete = json.dumps(json_complete, default=str, separators=(',', ':'), ensure_ascii=True)

            # res = str(json_complete)
            # print(res)
            return json_complete


    
    def send_to_matrix_json_do(self):
        xml_json_do = self.generate_json_l10n_do()
        xml_json = {"DO": xml_json_do}
        company = self.get_company()
        uuid = company.company_name
        rfc = self.company_id.partner_id.vat
        country = self.company_id.partner_id.country_id.code.lower()
        xml_json = {"from":uuid, "data":xml_json, "file_name": "132324277E310000000170"}
        mqtt_client = MqttClient("api.xmarts.com", 1883, prefix=f"uuid/{uuid}/rfc/{rfc}/country/{country}/", encryption_key=company.key)
        # xml_json = json.dumps(xml_json)
        print("send_to_matrix_json_do",xml_json)
        _logger.info(f"uuid/{uuid}/rfc/{rfc}/country/{country}/stamp")
        mqtt_client.send_message_serialized(
            [xml_json],
            f"uuid/{uuid}/rfc/{rfc}/country/{country}/stamp", 
            valid_json=True, 
            secure=True
        )

        time.sleep(1)
        self.refresh_account_move_xma()

    # -- Metodos  Localizacion MX -- 
    
    
    # -- Metodos  Localizacion PY --
    # def action_post(self):
    #     self._generate_pin()
    #     return super(AccountMove, self).action_post()
    
    def validate_fields_before_sign_py(self):
        if not self.l10n_xma_use_document_id:
            raise ValidationError(_('Error de llenado: Campo "Tipo de ingreso" es requerido'))
        
        if not self.l10n_xma_origin_operation_id:
            raise ValidationError(_('Error de llenado: Campo "Indicador de presencia" es requerido'))
        
        if not self.l10n_xma_issuance_type_id:
            raise ValidationError(_('Error de llenado: Campo "Tipo de emision" es requerido'))
        
        if not self.l10n_xma_payment_form:
            raise ValidationError(_('Error de llenado: Campo "Tipo de pago" es requerido'))
        
        if not self.l10n_xma_document_type:
            raise ValidationError(_('Error de llenado: Campo "Tipo de Documento" es requerido'))
        
        if self.sequence_number < self.l10n_xma_document_type.l10n_xma_sequence_start or self.sequence_number > self.l10n_xma_document_type.l10n_xma_sequence_end:
            raise ValidationError(_('El número de factura que se está emitiendo no se encuentra dentro del rango establecido por la SET'))
        # Partner_id
        if not self.partner_id.commercial_name:
            raise ValidationError(_('Error de llenado: Campo "Nombre Fantasia" en la ficha del cliente es requerido'))
        
        if not self.partner_id.name:
            raise ValidationError(_('Error de llenado: Campo "Nombre" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_control_digit:
            raise ValidationError(_('Error de llenado: Campo "Dígito de control del RUC" en la ficha del cliente es requerido'))
        
        if not self.partner_id.vat:
            raise ValidationError(_('Error de llenado: Campo "Identificacion Fiscal" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_customer_operation_type:
            raise ValidationError(_('Error de llenado: Campo "Tipo de operacion" en la ficha del cliente es requerido'))
        
        if not self.partner_id.state_id:
            raise ValidationError(_('Error de llenado: Campo "Departamento" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_city_id:
            raise ValidationError(_('Error de llenado: Campo "Ciudad" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_municipality_id:
            raise ValidationError(_('Error de llenado: Campo "Distrito" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_municipality_id:
            raise ValidationError(_('Error de llenado: Campo "Distrito" en la ficha del cliente es requerido'))
        
        if not self.partner_id.email:
            raise ValidationError(_('Error de llenado: Campo "Correo electronico" en la ficha del cliente es requerido'))
        
        if not self.partner_id.l10n_xma_taxpayer_type_id:
            raise ValidationError(_('Error de llenado: Campo "Distrito" en la ficha del cliente es requerido'))
        
        for lines in self.invoice_line_ids:
            if not lines.product_id.uom_id.l10n_xma_uomcode_id.code:
                raise ValidationError(_('Error de llenado: Campo "Codigo unidad de medida" en el producto %s (%s) es requerido ') % (str(lines.product_id.name), str(lines.product_id.uom_id.name)))
        
    def send_to_matrix_json(self):
        self.validate_fields_before_sign_py()
        xml_json_py = self.generate_json_l10n_py()
        xml_json = {"PY":xml_json_py}
        company = self.get_company()
        uuid = company.company_name
        rfc = self.company_id.partner_id.vat
        country = self.company_id.partner_id.country_id.code.lower()
        xml_json = {"from":uuid, "data":xml_json}
        _logger.info(f"uuid/{uuid}/rfc/{rfc}/country/{country}/stamp")
        mqtt_client = MqttClient("api.xmarts.com", 1883, prefix=f"uuid/{uuid}/rfc/{rfc}/country/{country}/", encryption_key=company.key)
        # xml_json = json.dumps(xml_json)
        mqtt_client.send_message_serialized(
            [xml_json],
            f"uuid/{uuid}/rfc/{rfc}/country/{country}/stamp", 
            valid_json=True, 
            secure=True
        )

        time.sleep(1)
        self.refresh_account_move_xma()
        self.l10n_xma_sif_status = 'sign'

    def consult_invoice_statur(self):
        dict_c = {"id": self.id, "data":{
                "NumDocumentoInicial": self.sequence_number,
                "NumDocumentoFinal": self.l10n_xma_document_type.l10n_xma_sequence_end,
                "CodTipoDocumento": self.l10n_xma_document_type.code,
                "NumTimbrado": self.l10n_xma_document_type.l10n_xma_authorization_code
            },
            "Parametros": {
                "AccImpresion": "S"
                }
            }
        json_complete = json.dumps(dict_c, default=str, separators=(',', ':'), ensure_ascii=True)
        print(json_complete, 'json_complete------------------------------------')
        # asyncio.run(self.async_send_message_status(json_complete))
    
    # async def async_send_message_status(self, data):
    #     server = self.company_id.matrix_server
    #     user = self.company_id.matrix_user
    #     password = self.company_id.matrix_password
    #     room_id = self.company_id.matrix_room

    #     client = AsyncClient(
    #         server,
    #         user,
    #         # "david.diaz",
    #         config={}
    #     ) 
    #     await client.login(password)
    #     # await client.login("gatitomaloxd")
    #     await client.room_send(
    #         room_id=room_id,
    #         message_type="m.room.message",
    #         content={
    #             "msgtype": "m.text",
    #             # "body": f'#stamp {json[1: -1]}',
    #             "body": f'#consultRuc {str(data)}',
    #         }
    #     )
    #     await client.close()

    def refresh_account_move_xma(self):
        print("REFRESH ACCOUNT")
        return {
            'name': _("Facturacion"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.id)],
            'target': 'current',
            'res_id': self.id,
        }
    
    # async def async_send_message_py(self, json):    
    #     server = self.company_id.matrix_server
    #     user = self.company_id.matrix_user
    #     password = self.company_id.matrix_password
    #     room_id = self.company_id.matrix_room

    #     client = AsyncClient(
    #         server,
    #         user,
    #         # "david.diaz",
    #         config={}
    #     ) 
    #     await client.login(password)
    #     # await client.login("gatitomaloxd")
    #     await client.room_send(
    #         room_id=room_id,
    #         message_type="m.room.message",
    #         content={
    #             "msgtype": "m.text",
    #             # "body": f'#stamp {json[1: -1]}',
    #             "body": f'#stamp {str(json)}',
    #         }
    #     )
    #     await client.close()
    
    def _generate_pin(self):

        pin_length = 9
        number_max = (10**pin_length) - 1
        number = randint(0, number_max)
        delta = (pin_length - len(str(number))) * '0'
        print('%s%s' % (delta, number))
        ramdom_code  = '%s%s' % (delta, number)
        condition = self.validate_ramdom_code(ramdom_code)
        if condition == True:
            self._generate_pin()
        self.ramdom_code = ramdom_code
    
    def validate_ramdom_code(self, code):
        acc = self.env['account.move'].search([('ramdom_code', '=', code)])
        if len(acc) >0:
            return True
        else: return False

    def generate_json_l10n_py(self):

        # actividadesEco = []
        ActividadesEconomicas = []
        for activities in self.company_id.l10n_xma_economic_activity_campany_id:
            # actividadesEco.append({
            #     "codigo": activities.code,
            #     "descripcion": activities.name,
            # })
            ActividadesEconomicas.append(
                {
                    "CodActividadEconomica": activities.code,
                    "DescActividadEconomica":activities.name,
                }
            )
        
        country_lines = self.partner_id.country_id
        items = []
        DatosItem = []
        for lines in self.invoice_line_ids:
            DatosItem.append({
                "CodPaisOrigen": country_lines.l10n_xma_country_code, #"PRY",
                "DescInformacionesAdicionales":lines.product_id.name, #"LICENCIAS ODOO",
                "CodUnidadMedidaItem": int(lines.product_id.uom_id.l10n_xma_uomcode_id.code), # 77
                "DescUnidadMeditaItem": lines.product_id.uom_id.l10n_xma_uomcode_id.name,
                "DatosIvaItem": {
                    "NumTasaIVA":  '%.8f' % (float(lines.tax_ids.amount)), # 10
                    "NumProporcionGravadaIVA": '%.8f' % (float(lines.tax_ids.l10n_xma_base_tax)), # 100
                    "MonLiquidacionIVA":  '%.8f' % (float((lines.quantity * lines.price_unit) -  (lines.price_subtotal * lines.quantity))),
                    "MonBaseGravadaIVA":  '%.8f' % (float(lines.price_subtotal)),
                    "CodAfectacionTributariaItem": 1
                },
                "DatosValorItem": {
                    "MonPrecioUnitarioItem":  '%.8f' % (float(lines.price_unit)), #17460655,
                    "MonTotalBrutoOperacionItem":  '%.8f' % (float(lines.price_unit)), #17460655,
                    "DatosValorRestaItem": {
                        "MonValorTotal":  '%.8f' % (float(lines.price_unit * lines.quantity)), #17460655,
                        "MonDescuentoItem":  '%.8f' % (float(lines.discount_balance)), # 0
                    }
                },
                "DescDescripcionItem": lines.name, #"LICENCIAS ODOO",
                "NumCantidadItem":  '%.4f' % (float(lines.quantity)), #1,
                "DescCodigoInternoItem": "1"
            })
            
        tipoRegimen = int(self.company_id.partner_id.l10n_xma_taxpayer_type_id.code)
        time_invoice = self.get_mx_current_datetime()
        str_time = time_invoice.strftime('%Y-%m-%dT%H:%M:%S')
        print(str_time)
        numero_documento = self.name.split('/')
        new_json = []
        json_new =  {
                "DatosAdicionales": {
                    "DescInformacionesAdicionales": "CORRESPONDIENTE A Julio 2023"
                },
                "IdDocumento": {
                    "NumTimbrado": int(self.l10n_xma_document_type.l10n_xma_authorization_code), #12559765,
                    "NumVersion": int(self.journal_id.version_document), #150,
                    "NumDocumento": int(str(self.sequence_number)), #26,
                    "FechEmision": str_time, #"2023-07-31T02:08:00",
                    "DescInformacionesDocumento": "Timbrado",
                    "CodMonedaOperacion": self.currency_id.name, #"PYG",
                    "CodPuntoExpedicion": self.l10n_xma_document_type.l10n_xma_dispatch_point, # "001",
                    "FechInicioTimbrado": self.company_id.start_date_post.strftime('%Y-%m-%d'), # "2023-07-31"
                    "CodTipoTransacion": 1,
                    "CodTipoDocumento":  int(self.l10n_xma_document_type.code), #1,
                    "CodTipoImpuesto": 1,
                    "CodTipoEmision": int(self.l10n_xma_issuance_type_id.code), #1
                },
                "Totales": {
                    "MonAnticipo": "0.00000000",
                    "MonDescuento": "0.00000000",
                    "MonBaseGravadaIVA10": str('%.8f' % (float(self.amount_untaxed))),  # "15873323.0000000",
                    "MonTotalBaseImponibleIVA":str( '%.8f' % (float(self.amount_untaxed))), # "15873323.0000000",
                    "MonSubTotalIVA10": str( '%.8f' % (float(self.amount_total))), #"17460655.00000000",
                    "MonTotalDescuento": "0.00000000",
                    "MonSubtotalExonerado": "0.00000000",
                    "MonTotalGeneral": str( '%.8f' % (float(self.amount_total))), #"17460650.00000000",
                    "MonLiquidacionIVA5": "0.00000000",
                    "MonSubtotalExento": "0.00000000",
                    "MonLiquidacionIVA10":str( '%.8f' % (float(self.amount_total - self.amount_untaxed))), # "1587332.00000000",
                    "MonTotalRedondeos": "0.0000",
                    "NumPorcentajeDescuentos": "0.00000000",
                    "MonSubTotalIVA5": "0.00000000",
                    "MonTotalOperacion": str( '%.8f' % (float(self.amount_total))), #"17460655.00000000",
                    "MonTotalLiquidacionIVA": str('%.8f' % (float(self.amount_total - self.amount_untaxed))), # "1587327.00000000"
                },
                # Partner
                "Receptor": {
                    "CodNaturalezaReceptor": 1,  #1,
                    "NumRUCReceptor": int(self.partner_id.vat), # 80055749,
                    "CodTipoOperacionReceptor": int(self.partner_id.l10n_xma_customer_operation_type), #1,
                    "CodTipoContribuyenteReceptor": 1, #1,
                    "CodPaisReceptor": self.partner_id.country_id.l10n_xma_country_code, # "PRY",
                    "CodDepartamentoReceptor": int(self.partner_id.state_id.code), ##11,
                    "CodDistritoReceptor": int(self.partner_id.l10n_xma_municipality_id.code), #145,
                    "CodCiudadReceptor": int(self.partner_id.l10n_xma_city_id.zipcode), #3432,
                    "DescNombreReceptor": self.partner_id.name, #"FERMAQ S.R.L.",
                    "DescDireccionReceptor": self.partner_id.street, # "KM. 15",
                    "NumDigitoVerificadorRUCReceptor": int(self.partner_id.l10n_xma_control_digit), # 2,
                    "NumNumeroCasaReceptor": self.partner_id.l10n_xma_external_number, # "1515"
                },
                "DatosItem": DatosItem,
                # Company
                "Emisor": {
                    "NumRUCEmisor": self.company_id.partner_id.vat , # "5448675",
                    "NumRucDigitoVerificadorEmisor": int(self.company_id.partner_id.l10n_xma_control_digit),#0,
                    "CodTipoContribuyenteEmisor": 1 if self.company_id.partner_id.company_type == 'person' else 2, #2,
                    "CodTipoRegimenEmisor": tipoRegimen, #,8,
                    "DescNombreEmisor": self.company_id.name, # "LIZBEL MARTINEZ SILVA",
                    "DescNombreFantasiaEmisor": self.company_id.partner_id.name, # "LIZBEL MARTINEZ SILVA",
                    "DescDirecionEmisor": self.company_id.partner_id.street, # "AMARRAS, COSTA DEL LAGO",
                    "NumNumeroCasaEmisor": self.company_id.partner_id.l10n_xma_external_number,  #"0",
                    "DescComplementoEmisor": self.company_id.partner_id.street, #"AMARRAS, COSTA DEL LAGO",
                    "DescComplemento2Emisor": self.company_id.partner_id.street2, #"SUPERCARRETERA",
                    "CodCiudadEmisor": int(self.company_id.partner_id.l10n_xma_city_id.zipcode),#3432,
                    "CodDistritoEmisor": int(self.company_id.partner_id.l10n_xma_municipality_id.code), #145,
                    "CodDepartamentoEmisor": int(self.company_id.partner_id.state_id.code), #11,
                    "NumTelefonoEmisor": self.company_id.partner_id.phone or "", #"0973527155",
                    "DescCorreoEmisor": self.company_id.partner_id.email or "", #"lizbelms@gmail.com",
                    "DescNombreInternoEmisor": self.company_id.partner_id.name, #"LIZBEL MARTINEZ SILVA",
                    "ActividadesEconomicas": ActividadesEconomicas,
                },
                
        }
        if self.l10n_xma_document_type.code in ('1','4'):
            json_new.update({
                "DatosPago": {
                    "CodCondicionOperacion": 1,
                    "DatosTipoPagoContado": [
                        {
                            "CodTipoPago": int(self.l10n_xma_payment_form.code), #1,
                            "DescTipoPago": self.l10n_xma_payment_form.name,
                            "MonPago": str(int(self.amount_total)) + ".0000", #  "17460655.0000",
                            "CodMoneda": self.currency_id.name, #"PYG",
                            "DescMoneda": self.currency_id.currency_unit_label, #"Guarani",
                            "MonTipoCambio": 0,
                            "PagoTarjeta": {},
                            "PagoCheque": {}
                        }
                    ]
                },
            })
        
        # new_json = json.dumps(new_json, default=str, separators=(',', ':'), ensure_ascii=True)
        if self.l10n_xma_cdc_asociado or self.l10n_xma_document_number_asociado and self.debit_origin_id:
            if self.l10n_xma_tipo_doc_asociado == '1':
                json_new.update({
                    "DocumentosAsociados":[{
                        "NumCDCAsociado": self.l10n_xma_cdc_asociado,
                        "DescTipoDocumentoAsociado": "Electrónico",
                        "CodTipoDocumentoAsociado":int(self.l10n_xma_tipo_doc_asociado),
                        
                    }],
                    "DatosEspecificosDocumento": {
                        "DatosNotaCreditoDebito":{
                            "CodMotivoEmision": int(self.l10n_mx_emi_motive),
                        },
                    },
                    
                })
            if self.l10n_xma_tipo_doc_asociado == '2':
                json_new.update({
                    "DocumentosAsociados":[{
                        "NumTimbradoAsociado":self.l10n_xma_number_timbrado_asociado, 
                        "DescTipoDocumentoAsociado": "Impreso",
                        "CodTipoDocumentoAsociado":int(self.l10n_xma_tipo_doc_asociado),
                        "CodEstablecimientoAsociado":self.l10n_xma_cod_state_asociado,
                        "CodPuntoExpedicionAsociado":self.l10n_xma_point_exp_asociado,
                        "NumDocumentoAsociado":self.l10n_xma_document_number_asociado,
                        "CodTipoDocumentoImpresoAsociado":int(self.l10n_document_type_asociado),
                        "FechDocumentoAsociado":self.l10n_xma_date_document_emision,
                        # "DescTipoDocumentoImpresoAsociado": "",
                        # "NumNumeroComprobanteRetencion": "",
                        # "NumResolucionCreditoFiscal": "",
                        # "CodTipoConstancia": 0,
                        # "DescTipoConstancia": "",
                        # "NumConstancia": 0,
                        # "NumControlConstancia": ""

                    }],
                    "DatosEspecificosDocumento": {
                        "DatosNotaCreditoDebito":{
                            "CodMotivoEmision": int(self.l10n_mx_emi_motive),
                    },
                },
                })
        else:
            json_new.update({
                "DatosEspecificosDocumento": {
                        "DatosFacturaElectronica": {
                            "CodTipoIndicadorPresencia": self.l10n_xma_origin_operation_id.code,
                        },
                    },
            })
        new_json.append(json_new)
        json_complete = {
            "id":self.id,
            "uuid_client":self.company_id.uuid_client,
            "data": new_json,
            "rfc": self.company_id.vat,
            "prod": 'NO',
            "type": 'PF',
        }

        return json_complete

    def delete_none_or_false(self, _dict):
        if isinstance(_dict, dict):
            for key, value in list(_dict.items()):
                if isinstance(value, (list, dict, tuple, set)):
                    _dict[key] = self.delete_none_or_false(value)
                elif value is None or key is None:
                    del _dict[key]

        elif isinstance(_dict, (list, set, tuple)):
            _dict = type(_dict)(self.delete_none_or_false(item) for item in _dict if item is not None)

        return _dict

    # -- Metodos  Localizacion PY --


    # -- Metodos Loca PE -- 
    @api.model
    def _l10n_xma_einvoice_pe_amount_to_text(self):
        self.ensure_one()
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = int(round(amount_d * 100, 2))
        words = num2words(amount_i, lang='es')
        result = '%(words)s Y %(amount_d)02d/100 %(currency_name)s' % {
            'words': words,
            'amount_d': amount_d,
            'currency_name':  self.currency_id.currency_unit_label,
        }
        return result.upper()

    def send_to_matrix_json_pe(self):
        pass

    def prepare_json_peru(self):
        

        json = {
            "Invoice": [
                {
                    "ext:UBLExtensions": [
                        {
                            "ext:UBLExtension": [
                                {"ext:ExtensionContent":[]}
                            ]
                        }
                    ],
                    "cbc:UBLVersionID": 2.1,
                    "cbc:CustomizationID": 2.0,
                    "cbc:ID": self.name,
                    "cbc:IssueDate": self.invoice_date,
                    "cbc:InvoiceTypeCode": self.l10n_xma_use_document_id.code,

                }
            ]
        }
        invoice_line = [] 
        for line in self.invoice_line_ids:
             invoice_line.append({
                "cbc:ID": 1,
                "cbc:InvoicedQuantity": 1,
                "cbc:LineExtensionAmount": 24.58,
                "cac:PricingReference": {
                    "cac:AlternativeConditionPrice": {
                    "cbc:PriceAmount": 29,
                    "cbc:PriceTypeCode": 1
                    }
                },
                "cac:TaxTotal": {
                    "cbc:TaxAmount": 4.42,
                    "cac:TaxSubtotal": {
                    "cbc:TaxableAmount": 24.58,
                    "cbc:TaxAmount": 4.42,
                    "cac:TaxCategory": {
                        "cbc:Percent": 18,
                        "cbc:TaxExemptionReasonCode": 10,
                        "cac:TaxScheme": {
                        "cbc:ID": 1000,
                        "cbc:Name": "IGV",
                        "cbc:TaxTypeCode": "VAT"
                        }
                    }
                    }
                },
                "cac:Item": {
                    "cbc:Description": "[00050050] TOFFEES SURTIDOS X 500 G TOF.SURTIDO 500 G",
                    "cac:CommodityClassification": ""
                },
                "cac:Price": {
                    "cbc:PriceAmount": 24.58
                }
            })
        js = {
            "Invoice": {
                "ext:UBLExtensions": {
                "ext:UBLExtension": {
                    "ext:ExtensionContent": []
                }
                },
                "cbc:UBLVersionID": 2.1,
                "cbc:CustomizationID": 2,
                "cbc:ID":self.name, # "F043-00009766",
                "cbc:IssueDate": self.invoice_date, # "2023-08-22",
                "cbc:InvoiceTypeCode": self.l10n_xma_document_type.code,
                "cbc:Note":  self._l10n_xma_einvoice_pe_amount_to_text(), #"VEINTINUEVE Y 00/100 SOLES",
                "cbc:DocumentCurrencyCode": self.currency_id.name, #"PEN",
                # "OrderReference": {
                # "ID": "2105 TIENDA AEROPUER"
                # },
                "cac:Signature": {
                    "cbc:ID":self.company_id.vat, # "IDSignKG",
                    "cac:SignatoryParty": {
                        "cac:PartyIdentification": {
                        "cbc:ID": self.company_id.vat, # 20100211115
                        },
                        "cac:PartyName": {
                        "cbc:Name": self.company_id.name, # "FAB DE CHOCOLATES LA IBERICA S A"
                        }
                    },
                    "cac:DigitalSignatureAttachmen": {
                        "cac:ExternalReference": {
                        "cbc:URI": "#SignVX"
                        }
                    }
                    },
                "cac:AccountingSupplierParty": {
                # "CustomerAssignedAccountID": 20100211115,
                    "cac:Party": {
                        "cac:PartyIdentification": {
                        "cbc:ID": self.company_id.vat, #20100211115
                        },
                        "cac:PartyName": {
                        "cbc:Name": self.company_id.vat, #"FAB DE CHOCOLATES LA IBERICA S A"
                        },
                        "cac:PartyLegalEntity": {
                        "cbc:RegistrationName": self.company_id.vat, #"FAB DE CHOCOLATES LA IBERICA S A",
                        "cac:RegistrationAddress": {
                            "cbc:ID": self.company_id.partner_id.l10n_xma_ubigeo_code, # 40101,
                            "cbc:AddressTypeCode": self.company_id.l10n_xma_address_type_code,
                            "cbc:StreetName": self.company_id.partner_id.street, # "AV. SANGARARA MZA. Q1 LOTE 34 URB. EL PINAR"
                        }
                        }
                    }
                },
                "cac:AccountingCustomerParty": {
                # "AdditionalAccountID": 6,
                "cac:Party": {
                    "cac:PartyIdentification": {
                        "cbc:ID": self.partner_id.vat, # 20336448337
                    },
                    "cac:PartyLegalEntity": {
                    "cbc:RegistrationName": self.partner_id.vat, # "TRANSPORTES Y COMERCIO SOL DEL PACIFICO E.I.R.L."
                    }
                }
                },
                # "PaymentTerms": {
                # "ID": "FormaPago",
                # "PaymentMeansID": "Contado"
                # },
                "cac:TaxTotal": {
                    "cbc:TaxAmount": 4.42,
                    "cac:TaxSubtotal": {
                        "cbc:TaxableAmount": 24.58,
                        "cbc:TaxAmount": 4.42,
                        "cac:TaxCategory": {
                            "cac:TaxScheme": {
                                "cbc:ID": 1000,
                                "cbc:Name": "IGV",
                                "cbc:TaxTypeCode": "VAT"
                            }
                        }
                    }
                },
                "cac:LegalMonetaryTotal": {
                    "cbc:LineExtensionAmount": 24.58,
                    "cbc:TaxInclusiveAmount": 29,
                    "cbc:PayableAmount": 29
                },
                "cac:InvoiceLine": invoice_line,
            }
        }
    
class AccountPayTerm(models.Model):
    _inherit = "account.payment.term"
    
    l10n_xma_payment_condition = fields.Selection([ ('1', 'plazo'),
                                                ('2', 'cuota'),],
                                               )
    
    l10n_xma_number = fields.Integer()