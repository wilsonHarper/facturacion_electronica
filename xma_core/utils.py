import json

from nio import MatrixRoom, RoomMessageText


def get_company(env):
    company_id = env['res.company'].search([("company_name", "!=", "")], limit=1)
    if not company_id:
        company_id = env['res.company'].search([], limit=1)

    return company_id


def get_http_uri_for_mxc(base_url: str, mxc: str) -> str:
    if not isinstance(mxc, str) or not mxc:
        return ''

    server_and_media_id = mxc[6:]
    prefix = '/_matrix/media/v1/download/'
    fragment_offset = server_and_media_id.find('#')
    fragment = ''
    if fragment_offset >= 0:
        fragment = server_and_media_id[fragment_offset:]
        server_and_media_id = server_and_media_id[:fragment_offset]
    return base_url + prefix + server_and_media_id + fragment


def process_once(env, prefix):
    def decorator(func):
        async def inner(room: MatrixRoom, message: RoomMessageText):
            if not message.body.startswith(prefix):
                return

            error = False
            relevant = True
            try:
                matrix_message = env['matrix.message'].search([('message_id', '=', message.event_id)], limit=1)
                if matrix_message and matrix_message.processed:
                    return
                relevant = await func(room, message)
            except Exception:
                error = True
            finally:
                if relevant:
                    env['matrix.message'].sudo().create({
                        'message_id': message.event_id,
                        'processed': True,
                        'error': error,
                    })
        return inner
    return decorator

def is_valid_json(payload: str) -> bool:
    try:
        json.loads(payload)
        return True
    except:
        return False