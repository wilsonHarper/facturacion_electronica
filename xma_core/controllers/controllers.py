# -*- coding: utf-8 -*-
import json
import random
import string
import asyncio
import traceback

from os import remove
from logging import getLogger

from cryptography.fernet import InvalidToken
from odoo import http
from odoo.http import request
# from nio import AsyncClient, ErrorResponse
# from ..utils import get_company


class AsyncIOController(http.Controller):

    def __init__(self):
        self.logger = getLogger("Controller")

    @http.route('/get-bot-id', type='http', auth="public", method=["GET"], csrf_token=False)
    def get_bot_id(self, **kw):
        company_id = request.env['res.company'].search([("matrix_user", "!=", "")], limit=1)

        return http.request.make_response(
            json.dumps({"bot_id": company_id.matrix_user}),
            headers=[
                ('Content-Type', 'application/json'),
            ]
        )

    @http.route('/wakeup', type='http', auth="public", method=["GET"], csrf_token=False)
    def wakeup(self, **kw):
        try:
            request.env['account.move'].sudo().master_callback()
        except InvalidToken:
            # This exception is raised when we try to log in with a different user

            self.logger.info(f"Trying to delete tmp session files..")

            self._delete_tmp_files()
            # Try again
            request.env['account.move'].sudo().master_callback()

        return http.request.make_response(
            json.dumps({"message": "Matrix bot shutdown"}),
            headers=[
                ('Content-Type', 'application/json'),
            ]
        )

    @http.route('/validate-axo', type='json', auth="public", method=["POST"], csrf_token=False)
    def validate(self, **kw):
        data = json.loads(request.httprequest.data)

        if 'key' not in data:
            return http.request.make_response(
                json.dumps({}),
                headers=[
                    ('Content-Type', 'application/json'),
                ],
                status=400
            )

        cred = request.env['res.users.apikeys'].sudo().check_credentials(scope=None, key=data['key'], env=request.env)

        return cred.user_id.name

    @http.route('/login-axo', type='json', auth="public", method=["POST"], csrf_token=False)
    def login(self, **kw):
        # myodoo.com/login-axo
        """
        Request
        {
            "user": "myuser",
            "password": "mypassword"
        }

        Response
        {
            "key": company_id.key,
            "uuid": company_id.company_name,
            "user_id": user.id
        }
        """

        credentials = json.loads(request.httprequest.data)

        if 'user' not in credentials or 'password' not in credentials:
            return http.request.make_response(
                json.dumps({"info": "Incorrect user or password"}),
                headers=[
                    ('Content-Type', 'application/json'),
                ],
                status=400
            )
        else:
            user = request.env['res.users'].sudo().search([('login', '=', credentials['user'])], limit=1)
            user.env.user = user

            parsed_user = {"id": user.id, "name": user.name, "room_id": user.room_id,
                           "rol": self.get_employee_from_user(user.id, request.env).job_id.name,
                           "rol_id": self.get_employee_from_user(user.id, request.env).job_id.id,
                           "employee_id": self.get_employee_from_user(user.id, request.env).id}

            try:
                user._check_credentials(credentials["password"], False)
                company_id = request.env['res.company'].search([("company_name", "!=", "")], limit=1)

                body = {"key": company_id.key, "uuid": company_id.company_name, "user_id": user.id}
                body.update(parsed_user)

                return body

            except Exception as e:
                traceback.print_exc()
                return http.request.make_response(
                    json.dumps({"info": "Incorrect user or password"}),
                    headers=[
                        ('Content-Type', 'application/json'),
                    ],
                    status=400
                )

    @http.route('/create-account', type='http', auth="public", method=["GET"], csrf_token=False)
    def create_account(self, **kw):
        company = self.get_company(request.env)
        name = f"{company.name} bot"

        # This is not secure, but it's just for testing
        letters = string.ascii_lowercase
        password = ''.join(random.choice(letters) for _ in range(10))

        # acc = asyncio.run(AsyncClient(company.matrix_server).register(name, password, company.name))

        # if isinstance(acc, ErrorResponse):
        #     return http.request.make_response(
        #         json.dumps({"message": "Error while creating account", "error": acc.message}),
        #         headers=[
        #             ('Content-Type', 'application/json'),
        #         ]
        #     )
        # else:
        #     company.write({
        #         "matrix_user": acc.user_id,
        #         "matrix_password": password,
        #     })
        #     return http.request.make_response(
        #         json.dumps({"user": name, "password": password, "server": company.matrix_server}),
        #         headers=[
        #             ('Content-Type', 'application/json'),
        #         ]
        #     )

    def _delete_tmp_files(self):
        file_paths = ["/tmp/session.txt", "/tmp/session_xma_core.txt"]
        # Delete files
        for file_path in file_paths:
            try:
                remove(file_path)
            except OSError:
                self.logger.info(f"Error while deleting file: {file_path}")


    def get_employee_from_user(self, user_id: int, env):
        employee = env['hr.employee'].sudo().search([
            ('user_id', '=', user_id)
        ], limit=1)

        if isinstance(employee, list) and len(employee) > 0:
            employee = employee[0]

        return employee
    

    def get_company(env):
        company_id = env['res.company'].search([("company_name", "!=", "")], limit=1)
        if not company_id:
            company_id = env['res.company'].search([], limit=1)

        return company_id
