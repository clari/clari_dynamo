# -*- coding: utf-8 -*-

import os
import sys
import requests
import simplejson
from clari_dynamo.conf.constants import *

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)
import cherrypy
from boto.dynamodb2.table import Table
from clari_dynamo.clari_dynamo import ClariDynamo
from clari_dynamo.migrate.run_migrations import migrate
from clari_dynamo.server import auth


class Server(object):
    def __init__(self, _db):
        self.db = _db
        migrate(self.db, MIGRATIONS_DIRECTORY)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        self.enforce_https_only()
        ret = HOME_TEXT
        ret['clari_dynamo']['tables'] = self.db.list_tables()
        return ret

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def put_item(self, table=None, tenant=None, purpose=None):
        if not cherrypy.request.method in ['PUT', 'POST']:
            raise cherrypy.HTTPError(400, 'Please send a PUT/POST request')
        else:
            self.validate_request(table=table, tenant=tenant, purpose=purpose)
            data = cherrypy.request.json
            ret = self.db.put_item(table, data, tenant, purpose)
            logging.info('creating a new item in ' + table)
            return ret

    @cherrypy.expose
    def get_item(self, table=None, tenant=None, purpose=None, attributes=None,
                 query=None):
        if not cherrypy.request.method == 'GET':
            raise cherrypy.HTTPError(400, 'Please send a GET request')
        else:
            self.validate_request(table=table, tenant=tenant,
                                  purpose=purpose, query=query)
            if attributes:
                attributes = json.loads(attributes)
            id_query = json.loads(query)
            ret = self.db.get_item(table, tenant, purpose, attributes,
                                   **id_query)
            logging.info('fetched item ' + table)
            ret = simplejson.dumps(ret._data, use_decimal=True)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return ret

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
            req.headers.get('X-Forwarded-Proto', '').lower() == 'https' or # Heroku / ELB
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

    def auth_passthrough(*args, **kwargs):
        ret = check_password(*args, **kwargs)
        return ret

    app_config = {
        '/': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'clari_dynamo_' + ENV_NAME.encode('ascii'),
            'tools.auth_basic.checkpassword': auth_passthrough,
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