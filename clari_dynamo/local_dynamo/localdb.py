# -*- coding: utf-8 -*-
from __future__ import print_function
import io
import zipfile
import subprocess
import requests

from clari_dynamo.conf.constants import *

URL =  'http://dynamodb-local.s3-website-us-west-2.amazonaws.com/dynamodb_local_latest.zip'
JAR =  'DynamoDBLocal.jar'
DIR = os.path.dirname(os.path.abspath(__file__))


class LocalDb(object):
    def __init__(self, port, in_memory=False):
        self.in_memory = in_memory
        if not os.path.isfile(DIR + '/' + JAR):
            logging.info('installing dynamo from ' + URL)
            r = requests.get(URL)
            z = zipfile.ZipFile(io.StringIO(r.content))
            z.extractall()
            logging.info('finished install')

        logging.info('starting dynamo local...')
        command_args = ['java',
                        '-Djava.library.path=' + DIR + '/DynamoDBLocal_lib',
                        '-jar', JAR,  '-port', str(port),  '-sharedDb',
                        '-dbPath', DIR]
        if in_memory:
            command_args.append('-inMemory')
        self.process = subprocess.Popen(command_args, cwd=DIR)
        logging.info('dynamo local started')
        self.up = True

    def __del__(self):
        if self.up:
            logging.warning(
                'last ditch effort to kill dynamo local, please call stop() '
                'instead')
            self.stop()

    def stop(self):
        logging.info('killing dynamo local')
        self.process.terminate()
        self.up = False

if __name__ == '__main__':
    local_db = LocalDb(port=8001, in_memory=True)
    local_db.stop()