import logging
import traceback


import MqttLibPy as mqtt

from odoo import _
from paho.mqtt.client import Client

from typing import Union, List
from datetime import datetime
import json
import base64
_logger = logging.getLogger(__name__)

class Routes:

    UPLOAD = "upload"
    STAMPED = "stamped"
    FAILED = "failed"
    SAVED = "saved"
    SYNCED = "synced"
    ERROR = "There was an error processing your request"
    WAITING = "waiting"

    def __init__(self, client: mqtt.client.MqttClient, env, company_id, prefix=''):
        self.logger = logging.getLogger("Command")
        self.client = client
        self.prefix = prefix

        @client.endpoint(prefix + "test", force_json=True, secure=True)
        def test_route(client: Client, _, message: Union[List[dict], dict]):
            print(message)
            self.logger.info("> Test route hit! <")

        @client.endpoint(prefix + self.WAITING, force_json=True, secure=True)
        def waiting(client: Client, _, json_data):
            env.cr.commit()
            print("JSON1-------------------------\n", json_data)
            json_data = json_data[0]
            filename = str(json_data['xml_name'])
            country = json_data['country']
            filename = filename.split('.')[0]
            rfc = filename.split('_')[0]
            if country == "br":
                rfc = "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(*rfc)
            type_xml = filename.split('_')[2]
            comp = env['res.company'].sudo().search([
                ('vat', '=', rfc) ], limit=1)
            if comp:
                if type_xml == 'BF':
                    id_factura = int(filename.split('_')[1])
                    account_move = env['account.move'].sudo().search([
                        ('id', '=', id_factura)
                    ], limit=1)
                    # xml_byte = json_data['bytes']
                    # xml_byte = json_data['bytes'].decode("utf-8")
                    # xml_byte = xml_byte.replace('&', '&amp;')
                    # xml_byte = xml_byte.encode('utf-8')
                    # xml_attachment = env['ir.attachment'].sudo().create({
                    #     'name': account_move.name + str('.xml'),
                    #     'type': 'binary',
                    #     'datas': base64.b64encode(xml_byte),
                    #     'res_model': 'account.move',
                    #     'res_id': id_factura,
                    #     'mimetype': 'application/xml'
                    # })
                    # xml_byte = json_data['bytes'].decode("utf-8").replace("Antig\xc3\xbcedad", "Antigüedad")
                    # account_move.l10n_xma_invoice_cfdi = base64.b64encode(xml_byte)
                    # account_move.l10n_xma_invoice_cfdi_name = account_move.name + str('.xml')
                    account_move.message_post(
                        body="""<p> Factura en proceso de revision.</p>""",
                        attachment_ids=[]
                    )
                    env.cr.commit()

        @client.endpoint(prefix + self.UPLOAD, is_file=True, secure=True)
        def upload(client: Client, _, json_data):
            env.cr.commit()
            print("json_data", json_data)
            filename = str(json_data['filename'])
            filename = filename.split('.')[0]
            rfc = filename.split('_')[0]
            type_xml = filename.split('_')[2]
            if type_xml == 'BF':
                rfc = "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(*rfc)
            
            comp = env['res.company'].sudo().search([
                ('vat', '=', rfc)
            ], limit=1)
            if comp:
                if type_xml == 'BF':
                    id_factura = int(filename.split('_')[1])
                    account_move = env['account.move'].sudo().search([
                        ('id', '=', id_factura)
                    ], limit=1)
                    file_ext = json_data['filename'].split(".")[1]
                    if file_ext == 'xml':
                        xml_byte = json_data['bytes']
                        xml_byte = json_data['bytes'].decode("utf-8")
                        xml_byte = xml_byte.replace('&', '&amp;')
                        xml_byte = xml_byte.encode('utf-8')
                        xml_attachment = env['ir.attachment'].sudo().create({
                            'name': account_move.name + str('.xml'),
                            'type': 'binary',
                            'datas': base64.b64encode(xml_byte),
                            'res_model': 'account.move',
                            'res_id': id_factura,
                            'mimetype': 'application/xml'
                        })
                        # xml_byte = json_data['bytes'].decode("utf-8").replace("Antig\xc3\xbcedad", "Antigüedad")
                        account_move.l10n_xma_invoice_cfdi = base64.b64encode(xml_byte)
                        account_move.l10n_xma_invoice_cfdi_name = account_move.name + str('.xml')
                        account_move.message_post(
                            body="""<p></p>""",
                            attachment_ids=[xml_attachment.id]
                        )
                    if file_ext == 'pdf':
                        pdf_byte = json_data['bytes']
                        pdf_attachment = env['ir.attachment'].sudo().create({
                            'name': account_move.name + str('.pdf'),
                            'type': 'binary',
                            'datas': base64.b64encode(pdf_byte),
                            'res_model': 'account.move',
                            'res_id': id_factura,
                            'mimetype': 'application/x-pdf'
                        })
                        account_move.message_post(
                            body="""<p></p>""",
                            attachment_ids=[pdf_attachment.id]
                        )
                    env.cr.commit()
                if type_xml == 'DF':
                    id_factura = int(filename.split('_')[1])
                    account_move = env['account.move'].sudo().search([
                        ('id', '=', id_factura)
                    ], limit=1)
                    xml_byte = json_data['bytes']
                    xml_byte = json_data['bytes'].decode("utf-8")
                    xml_byte = xml_byte.replace('&', '&amp;')
                    xml_byte = xml_byte.encode('utf-8')
                    xml_attachment = env['ir.attachment'].sudo().create({
                        'name': account_move.name + str('.xml'),
                        'type': 'binary',
                        'datas': base64.b64encode(xml_byte),
                        'res_model': 'account.move',
                        'res_id': id_factura,
                        'mimetype': 'application/xml'
                    })
                    # xml_byte = json_data['bytes'].decode("utf-8").replace("Antig\xc3\xbcedad", "Antigüedad")
                    account_move.l10n_xma_invoice_cfdi = base64.b64encode(xml_byte)
                    account_move.l10n_xma_invoice_cfdi_name = account_move.name + str('.xml')
                    account_move.message_post(
                        # body="""<p> Servicio de firma  Exitoso. </p>""",
                        attachment_ids=[xml_attachment.id]
                    )
                    env.cr.commit()
                if type_xml == 'F':
                    id_factura = int(filename.split('_')[1])
                    account_move = env['account.move'].sudo().search([
                        ('id', '=', id_factura)
                    ], limit=1)
                    xml_byte = json_data['bytes']
                    xml_byte = json_data['bytes'].decode("utf-8")
                    xml_byte = xml_byte.replace('&', '&amp;')
                    xml_byte = xml_byte.encode('utf-8')
                    xml_attachment = env['ir.attachment'].sudo().create({
                        'name': account_move.name + str('.xml'),
                        'type': 'binary',
                        'datas': base64.b64encode(xml_byte),
                        'res_model': 'account.move',
                        'res_id': id_factura,
                        'mimetype': 'application/xml'
                    })
                    # xml_byte = json_data['bytes'].decode("utf-8").replace("Antig\xc3\xbcedad", "Antigüedad")
                    account_move.l10n_xma_invoice_cfdi = base64.b64encode(xml_byte)
                    account_move.l10n_xma_invoice_cfdi_name = account_move.name + str('.xml')
                    account_move.message_post(
                        body="""<p> Servicio de firma  Exitoso. </p>""",
                        attachment_ids=[xml_attachment.id]
                    )
                    env.cr.commit()
                if type_xml == 'P':
                        id_payment = int(filename.split('_')[1])
                        account_payment = env['account.payment'].sudo().search([
                            ('id', '=', id_payment)
                        ], limit=1)
                        xml_byte = json_data['bytes']
                        xml_byte = json_data['bytes'].decode("utf-8")
                        xml_byte = xml_byte.replace('&', '&amp;')
                        xml_byte = xml_byte.encode('utf-8')
                        xml_attachment = env['ir.attachment'].sudo().create({
                            'name': account_payment.name + str('.xml'),
                            'type': 'binary',
                            'datas': base64.b64encode(xml_byte),
                            'res_model': 'account.payment',
                            'res_id': id_payment,
                            'mimetype': 'application/xml'
                        })
                        account_payment.l10n_xma_payment_cfdi = base64.b64encode(json_data['bytes'])
                        account_payment.l10n_xma_payment_cfdi_name = account_payment.name + str('.xml')
                        account_payment.message_post(
                            body="""<p> Servicio de firma  Exitoso. </p>""",
                            attachment_ids=[xml_attachment.id]
                        )
                        env.cr.commit()
                if type_xml == 'D':
                        id_stock = int(filename.split('_')[1])
                        stock_picking = env['stock.picking'].sudo().search([
                            ('id', '=', id_stock)
                        ], limit=1)
                        xml_byte = json_data['bytes']
                        xml_byte = json_data['bytes'].decode("utf-8")
                        print(xml_byte)
                        xml_byte = xml_byte.replace('&', '&amp;')\
                            .replace('\xc3\xad', 'í').replace('\\xc3\\xad','í').\
                                replace('\xc3\xa9','é').replace('\\xc3\\xa9', 'é')
                        xml_byte = xml_byte.encode('utf-8')
                        print(xml_byte)
                        xml_attachment = env['ir.attachment'].sudo().create({
                            'name': stock_picking.name + str('.xml'),
                            'type': 'binary',
                            'datas': base64.b64encode(xml_byte),
                            'res_model': 'stock.picking',
                            'res_id': id_stock,
                            'mimetype': 'application/xml'
                        })
                        stock_picking.edi_cfdi = base64.b64encode(json_data['bytes'])
                        stock_picking.edi_cfdi_name = stock_picking.name + str('.xml')
                        stock_picking.message_post(
                            body="""<p> Servicio de firma  Exitoso. </p>""",
                            attachment_ids=[xml_attachment.id]
                        )
                        env.cr.commit()
                if type_xml == 'N':
                        id_nomina = int(filename.split('_')[1])
                        hr_payslip = env['hr.payslip'].sudo().search([
                            ('id', '=', id_nomina)
                        ], limit=1)
                        xml_byte = json_data['bytes'].decode("utf-8")
                        xml_byte = xml_byte.replace("Antig\xc3\xbcedad", "Antigüedad").replace("Antig\\xc3\\xbcedad","Antigüedad").replace('&', '&amp;')
                        xml_byte = xml_byte.encode('utf-8')

                        xml_attachment = env['ir.attachment'].sudo().create({
                            'name': hr_payslip.name + str('.xml'),
                            'type': 'binary',
                            'datas': base64.b64encode(xml_byte),
                            'res_model': 'hr.payslip',
                            'res_id': id_nomina,
                            'mimetype': 'application/xml'
                        }) 
                        # NOTE revisar el modulo de nomina y agregar los campos para 
                        # almacenamiento de la nomina(xml) y de la cadena original

                        hr_payslip.l10n_xma_invoice_cfdi = base64.b64encode(xml_byte)
                        hr_payslip.l10n_xma_invoice_cfdi_name = hr_payslip.name + str('.xml')
                        hr_payslip.message_post(
                            body="""<p> Servicio de firma  Exitoso. </p>""",
                            attachment_ids=[xml_attachment.id]
                        )
                        env.cr.commit()
                if type_xml == 'PF':
                        id_factura = int(filename.split('_')[1])
                        account_move = env['account.move'].sudo().search([
                            ('id', '=', id_factura)
                        ], limit=1)
                        xml_byte = json_data['bytes']
                        xml_byte = json_data['bytes'].decode("utf-8")
                        xml_byte = xml_byte.replace('&', '&amp;')
                        xml_byte = xml_byte.encode('utf-8')
                        xml_attachment = env['ir.attachment'].sudo().create({
                            'name': account_move.name + str('.xml'),
                            'type': 'binary',
                            'datas': base64.b64encode(xml_byte),
                            'res_model': 'account.move',
                            'res_id': id_factura,
                            'mimetype': 'application/xml'
                        })
                        account_move.l10n_xma_xml_ar = base64.b64encode(json_data['bytes'])
                        account_move.l10n_xma_xml_name = account_move.name + '.xml'
                        account_move.message_post(
                            body="""<p> Servicio de firma  Exitoso. </p>""",
                            attachment_ids=[xml_attachment.id]
                        )
                        env.cr.commit()

        @client.endpoint(prefix + self.STAMPED, force_json=True, secure=True)
        def stamped(client: Client, _, json_data: Union[List[dict], dict]):
            try:
                json_data = json_data[0]
                country = json_data['country']
                rfc = ''
                if country == 'do':
                    rfc = json_data['rfc']
                if country == 'py':
                    rfc = json_data['rfc'].split('-')[0]
                if country == 'mx':
                    rfc = json_data['rfc']
                if country == "br":
                    rfc = "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(*rfc)
                comp = env['res.company'].sudo().search([
                    ('vat', '=', rfc)
                ], limit=1)
                msg = "#stamped: -------------------------------" + str(comp.vat)
                _logger.info(msg)
                env.cr.commit()
                if comp:
                    if json_data['description']['type'] == 'BF':
                        account_move = env['account.move'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        # account_move.is_einvoice_send = True
                        # account_move.l10n_xma_edi_einvoice = json_data['description']['Id']
                        # account_move.l10n_xma_uuid_invoice = json_data['description']['NumCDC']
                        env.cr.commit()
                    if json_data['description']['type'] == 'DF':
                        acc = env['account.move'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)

                        print("+++++++++++++++++++++++++++++++++++++",acc)
                        # acc.l10n_xma_timbre = True
                        # acc.l10n_xma_cadena_original = json_data['description']['cadenaOriginal']
                        # cadenaoriginalsp = json_data['description']['cadenaOriginal'].split('|')[3]
                        # acc.l10n_xma_uuid_invoice = cadenaoriginalsp
                        # datetime_str = json_data['datetime'].replace('T', ' ')
                        for iter in json_data['description']['DGII_response']['mensajes']:
                            valor = iter['valor']
                            codigo = iter['codigo']
                            acc.message_post(
                                body=(
                                    """<p>Codigo:</p><p><ul>%s</ul></p>""" %
                                    codigo))
                            acc.message_post(
                                body=(
                                    """<p>Valor:</p><p><ul>%s</ul></p>""" %
                                    valor))
                            
                        acc.message_post(
                            body=(
                                """<p>TrackId:</p><p><ul>%s</ul></p>""" %
                                json_data['description']['DGII_response']['trackId']))
                        acc.message_post(
                            body=(
                                """<p>Estado:</p><p><ul>%s</ul></p>""" %
                                json_data['description']['DGII_response']['estado']))
                        acc.message_post(body=(
                                """<p>El servicio de firma solicitado falló. </p>"""))
                        
                        env.cr.commit()
                    if json_data['description']['type'] == 'F':
                        acc = env['account.move'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        acc.l10n_xma_timbre = True
                        acc.l10n_xma_cadena_original = json_data['description']['cadenaOriginal']
                        cadenaoriginalsp = json_data['description']['cadenaOriginal'].split('|')[3]
                        acc.l10n_xma_uuid_invoice = cadenaoriginalsp
                        datetime_str = json_data['datetime'].replace('T', ' ')
                        print(type(datetime_str))
                        print(datetime_str)
                        date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                        acc.l10n_xma_post_time = date
                        env.cr.commit()
                    if json_data['description']['type'] == 'PF':
                        account_move = env['account.move'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        account_move.is_einvoice_send = True
                        account_move.l10n_xma_edi_einvoice = json_data['description']['Id']
                        account_move.l10n_xma_uuid_invoice = json_data['description']['NumCDC']
                        env.cr.commit()
                    if json_data['description']['type'] == 'D':
                        stock_picking = env['stock.picking'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        stock_picking.edi_cadena_original = json_data['description']['cadenaOriginal']
                        cadenaoriginalsp = json_data['description']['cadenaOriginal'].split('|')[3]
                        stock_picking.l10n_sing = True
                        stock_picking.l10n_xma_electronic_number = cadenaoriginalsp
                        env.cr.commit()
                    if json_data['description']['type'] == 'P':
                        account_payment = env['account.payment'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        account_payment.l10n_xma_timbre = True
                        account_payment.l10n_xma_cadena_original = json_data['description']['cadenaOriginal']
                        cadenaoriginalsp = json_data['description']['cadenaOriginal'].split('|')[3]
                        account_payment.l10n_xma_uuid_invoice = cadenaoriginalsp
                        datetime_str = json_data['datetime'].replace('T', ' ')
                        print(type(datetime_str))
                        print(datetime_str)
                        date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                        account_payment.l10n_xma_post_time = date
                        env.cr.commit()
                    if json_data['description']['type'] == 'N':
                        nomina = env['hr.payslip'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        # NOTE revisar los campos ha llenar en el modulo de la nomina
                        nomina.l10n_xma_timbre = True
                        nomina.l10n_xma_cadena_original = json_data['description']['cadenaOriginal']
                        cadenaoriginalsp = json_data['description']['cadenaOriginal'].split('|')[3]
                        nomina.l10n_xma_uuid_invoice = cadenaoriginalsp
                        datetime_str = json_data['datetime'].replace('T', ' ')
                        print(type(datetime_str))
                        print(datetime_str)
                        date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                        # nomina.l10n_xma_post_time = date
                        env.cr.commit()
            except Exception as err:
                print(err)
                payload = [{"message": str(err)}]
                self.client.send_message_serialized(payload, self.STAMPED, error=True, valid_json=True)

        @client.endpoint(prefix + self.FAILED, force_json=True, secure=True)
        def failed(client: Client, __, json_data: Union[List[dict], dict]):
            
            try:
                _logger.info(json_data[0])
                json_data = json_data[0]
                country = json_data['country']
                rfc = ''
                if country == 'do':
                    rfc = json_data['rfc'].split('-')[0]
                if country == 'py':
                    rfc = json_data['rfc'].split('-')[0]
                if country == 'mx':
                    rfc = json_data['rfc']
                if country == "br":
                    rfc = "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(*json_data['rfc'])
                comp = env['res.company'].sudo().search([
                    ('vat', '=', rfc)
                ], limit=1)
                msg = "Error in #stamped: -------------------------------" + str(comp.vat)
                _logger.info(msg)
                print(comp.vat)
                if comp:
                    if json_data['description']['type'] == 'BF':
                        acc = env['account.move'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        self.logger.info(acc.name)
                        self.logger.info(json_data['description']['response'])
                        acc.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'FD':
                        acc = env['account.move'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        self.logger.info(acc.name)
                        self.logger.info(json_data['description']['response'])
                        acc.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'F':
                        acc = env['account.move'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        self.logger.info(acc.name)
                        self.logger.info(json_data['description']['response'])
                        acc.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'D':
                        stock_picking = env['stock.picking'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        stock_picking.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'P':
                        account_payment = env['account.payment'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        print(account_payment.name)
                        account_payment.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'N':
                        nomina = env['hr.payslip'].search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        nomina.message_post(
                            body=_(
                                """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                json_data['description']['response']))
                        env.cr.commit()
                    if json_data['description']['type'] == 'PF':
                        account_move = env['account.move'].sudo().search([
                            ('id', '=', json_data['id'])
                        ], limit=1)
                        for error in json_data['description']['response']:
                            account_move.message_post(
                                body=_(
                                    """<p>El servicio de firma solicitado falló. </p><p><ul>%s</ul></p>""" %
                                    error['DescRetorno']))
                            env.cr.commit()


            except Exception as err:
                payload = {"message": str(err)}
                traceback.print_exc()
                self.client.send_message_serialized([payload], self.FAILED, error=True, valid_json=True)
            env.cr.commit()

        @client.endpoint(prefix + self.SAVED, force_json=True, secure=True)
        def saved(client: Client, _, json_data: Union[List[dict], dict]):
            try:
                json_data = json_data[0]
                if company_id.partner_id.vat == json_data['rfc']:
                    certs = env['certificate'].search([], limit=1)
                    print(certs.holder_vat)
                    certs.sync_status = 'saved'
                    # json_sync = {
                    # "id":certs.id,
                    # "partner_id":company_id.uuid_client,
                    # "company_name":company_id.name,
                    # "country_code":company_id.partner_id.country_id.code,
                    # }
                    # json_sync = json.dumps(json_sync, default=str, separators=(',', ':'), ensure_ascii=False)
                    # json_string = f'#sync {str(json_sync)}'
                    # await bot.api.send_text_message(room.room_id, json_string)
                    env.cr.commit()
            except Exception as err:
                payload = {"message": str(err)}
                self.client.send_message_serialized([payload], self.SAVED, error=True, valid_json=True)

        @client.endpoint(prefix + self.SYNCED, force_json=True, secure=True)
        def synced(client: Client, _, json_data: Union[List[dict], dict]):
            try:
                json_data = json_data[0]
                if company_id.partner_id.vat == json_data['rfc']:
                    certs = env['certificate'].search([], limit=1)
                    print(certs.holder_vat)
                    if certs:
                        certs.sync_status = 'sync'
                        env.cr.commit()
            except Exception as err:
                payload = {"message": str(err)}
                self.client.send_message_serialized([payload], self.SYNCED, error=True, valid_json=True)

    def _send_serialized_messages(self, command_name: str, data: Union[list[dict], str],
                                  route, encode=False, valid_json=False, error=False, message_id=0, secure=True):
        self.client.send_message_serialized(data, route, valid_json=valid_json, error=error, secure=secure)
