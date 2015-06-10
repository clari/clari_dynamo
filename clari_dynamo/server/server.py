# -*- coding: utf-8 -*-

import os
import sys
import requests
from clari_dynamo.conf.constants import *

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)
import cherrypy
from boto.dynamodb2.table import Table
from clari_dynamo.clari_dynamo import ClariDynamo
import auth


class Server(object):
    def __init__(self, _db):
        self.db = _db

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        self.enforce_https_only()
        return HOME_TEXT

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def put_item(self, table=None, tenant=None, purpose=None):
        if not cherrypy.request.method in ['PUT', 'POST']:
            raise cherrypy.HTTPError(400, 'Please send a PUT/POST request')
        else:
            self.validate_request(table=table, tenant=tenant, purpose=purpose)
            data = cherrypy.request.json
            _table = Table(table)
            self.db.put_item(_table, data, tenant)
            logging.info('creating a new item in ' + table)
            return { 'success': True }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_item(self, table=None, tenant=None, purpose=None, query=None):
        if not cherrypy.request.method == 'GET':
            raise cherrypy.HTTPError(400, 'Please send a GET request')
        else:
            self.validate_request(table=table, tenant=tenant,
                                  purpose=purpose, query=query)
            id_query = json.loads(query)
            _table = Table(table)
            ret = self.db.get_item(_table, tenant, **id_query)
            logging.info('fetched item ' + table)
            return str(ret)

    def log_headers(self):
        headers = cherrypy.request.headers
        filtered_headers = {}
        for name in cherrypy.request.headers:
            if name.lower().find('auth') == -1:
                filtered_headers[name] = headers[name]
            else:
                headers[name] = '[FILTERED]'  # Don't let anyone else log this.
        logging.info(filtered_headers)

    def enforce_https_only(self):
        self.log_headers()
        req = cherrypy.request
        assert (
            req.scheme.lower() == 'https' or
            req.headers.get('X-Forwarded-Proto', '').lower() == 'https' or
            ENV_NAME == 'dev'
        )

    def validate_request(self, **kwargs):
        for arg in kwargs:
            assert kwargs[arg], ('must define "%s" query string param' % arg)
        self.enforce_https_only()
        auth.check(cherrypy)


def handle_error(**kwargs):
    msg = "Smokey bananas, something's off. Check the logs..."
    cherrypy.response.body = [msg]
    return msg


cherrypy.config.update({
    'server.socket_host':       '0.0.0.0',  # Trust your Wi-Fi?
    'server.socket_port':       int(os.environ.get('PORT', '55555')),
    'server.thread_pool':       150,  # Number of parallel requests
    'server.socket_queue_size': 200,  # Number of requests that can wait for a thread
    'server.socket_timeout':    20,
})

if HIDE_ERRORS:
    # Don't return error messages in response for 500's
    cherrypy.config.update({'request.error_response':   handle_error})

    # Don't return error messages in response for 400's
    for i in range(100):
        cherrypy.config.update({'error_page.' + str(400 + i): handle_error})


if not AUTH_WEB_HOOK and BASIC_AUTH_DICT:
    check_password = cherrypy.lib.auth_basic.checkpassword_dict(BASIC_AUTH_DICT)
    app_config = {
        '/': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'clari_dynamo_' + ENV_NAME.encode('ascii'),
            'tools.auth_basic.checkpassword': check_password,
        },
    }
else:
    app_config = None

db_conf = {
    'aws_access_key':        AWS_ACCESS_KEY_ID,
    'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
    'is_remote':             IS_REMOTE,
    'is_secure':             DYNAMO_IS_SECURE}

if not IS_REMOTE:
    db_conf['host'] = 'localhost'
    db_conf['port'] = 8000

cherrypy.tree.mount(Server(ClariDynamo(**db_conf)), '/', config=app_config)
cherrypy.engine.start()