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
    def table(self, name, tenant_id=None, purpose=None):
        self.validate_request(purpose, tenant_id)
        if cherrypy.request.method in ['PUT', 'POST']:
            data = cherrypy.request.json
            table = Table(name)
            self.db.put_item(table, data)
            logging.info('creating a new item in ' + name)
        return { 'success': True }

    def enforce_https_only(self):
        assert cherrypy.request.scheme == 'https' or ENV_NAME == 'dev'

    def validate_request(self, purpose, tenant_id):
        assert tenant_id, 'must define "tenant_id" query string param'
        assert purpose, 'must define "purpose" query string param'
        self.enforce_https_only()
        auth.check(cherrypy)

cherrypy.config.update({
    'server.socket_host':       '0.0.0.0',  # Trust your Wi-Fi?
    'server.socket_port':       int(os.environ.get('PORT', '55555')),
    'server.thread_pool':       150,  # Number of parallel requests
    'server.socket_queue_size': 200,  # Number of requests that can wait for a thread
    'server.socket_timeout':    20,
})

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