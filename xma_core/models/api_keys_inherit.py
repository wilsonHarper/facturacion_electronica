import os
import binascii

from passlib.context import CryptContext
from odoo.models import Model


KEY_CRYPT_CONTEXT = CryptContext(
    # default is 29000 rounds which is 25~50ms, which is probably unnecessary
    # given in this case all the keys are completely random data: dictionary
    # attacks on API keys isn't much of a concern
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)


class APIKeys(Model):

    _name = 'res.users.apikeys'
    _inherit = 'res.users.apikeys'

    def generate_key(self, scope, name, user_id):
        """Generates an api key.
        :param str scope: the scope of the key. If None, the key will give access to any rpc.
        :param str name: the name of the key, mainly intended to be displayed in the UI.
        :return: str: the key.

        """
        # no need to clear the LRU when *adding* a key, only when removing
        k = binascii.hexlify(os.urandom(20)).decode()
        self.env.cr.execute("""
        INSERT INTO {table} (name, user_id, scope, key, index)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """.format(table=self._table),
                            [name, user_id, scope, KEY_CRYPT_CONTEXT.hash(k), k[:8]])

        # ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'

        return k

    def check_credentials(self, *, scope, key, env):
        # assert scope, "scope is required"
        index = key[:8]
        self.env.cr.execute('''
            SELECT user_id, key
            FROM {} INNER JOIN res_users u ON (u.id = user_id)
            WHERE u.active and index = %s AND (scope IS NULL OR scope = %s)
        '''.format(self._table),
        [index, scope])
        for user_id, current_key in self.env.cr.fetchall():
            if KEY_CRYPT_CONTEXT.verify(key, current_key):
                return env['res.users'].search([('id', '=', user_id)], limit=1)
