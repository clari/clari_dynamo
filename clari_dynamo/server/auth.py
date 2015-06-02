# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function,unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import requests
from clari_dynamo.conf.constants import *
import json


def should_forward_auth_check(cherrypy, tenant_id):
    encrypted_cached_auth_cookie = cherrypy.request.cookie[
        'clari_dynamo.cached_auth.' + ENV_NAME]

    if encrypted_cached_auth_cookie is None:
        return True
    else:
        cached_auth_cookie = CRYPTO.decrypt(encrypted_cached_auth_cookie)
        if cached_auth_cookie.is_expired():
            return False
        else:
            check_tenant_id = json.loads(cached_auth_cookie)['tenant_id']
            if check_tenant_id != tenant_id:
                raise cherrypy.HTTPError(401,
                    'You are not authorized to access that resource')
            else:
                return True


def forward_auth_check(cherrypy, tenant_id):
    # Cookie forwarded from authorization server
    forwarded_cookie = cherrypy.request.cookie[
        'clari_dynamo.' + ENV_NAME + '.forwarded']
    # Expects Cookie: clari_dynamo.production.forwarded=name|value
    forwarded_cookie_name, forwarded_cookie_value = \
        forwarded_cookie.split('|')
    status_code = requests.get(AUTH_WEB_HOOK % str(tenant_id), cookies={
        forwarded_cookie_name: forwarded_cookie_value}).status_code
    if status_code != 200:
        raise cherrypy.HTTPError(401,
                            'You are not authorized to access that resource')
    else:
        pass
        # TODO: set_cookie(tenant_id)

if AUTH_WEB_HOOK:
    def check(cherrypy, tenant_id):
        if should_forward_auth_check(cherrypy, tenant_id):
            forward_auth_check(cherrypy, tenant_id)
else:
    # Basic auth done by cherrypy.
    check = lambda *args: True
