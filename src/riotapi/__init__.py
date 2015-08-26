from _collections import defaultdict
import lolstatic
print("Imported", __name__)

import urllib3
import certifi
import json
import time
import sys
from optparse import OptionParser
from threading import Lock
from .RateLimit import RateLimit

parser = OptionParser()
parser.add_option("-f", "--failed", action="store_false", dest="ignoreFailedFiles",
                  default=True, help="Retry previously failed game ids")
parser.add_option("-k", default = False, action="store", dest="key", type="string", help="Retry previously failed game ids")
if not parser.parse_args(sys.argv)[0].key:
    print("To work correctly, the api needs to have a key")
    sys.exit(-1)

class AnswerException(Exception):
    def __init__(self, msg, answer):
        Exception(msg)
        self.msg = msg
        self.answer = answer

class Downloader():
    def __init__(self):  
        self.limit_fast = RateLimit(3000, 12.0)
        self.limit_slow = RateLimit(180000, 620.0)
        self.lock = Lock()
        
        global parser
        self.key = parser.parse_args(sys.argv)[0].key # Ask for a key to avoid storing it
        
        self.api = urllib3.PoolManager(          # https connector
            cert_reqs='CERT_REQUIRED', # Force certificate check.
            ca_certs=certifi.where(),  # Path to the Certifi bundle.
            maxsize = 3,
            num_pools = 10
        )
    

    def api_request(self, region, path, fields = None, **data):
        self.limit_fast.inc()
        self.limit_slow.inc()
        url = "https://{region}.api.pvp.net{path}".format(region = region, path = path)
        data['api_key'] = self.key
        url += '?' + '&'.join(str(arg) + '=' + str(data[arg]) for arg in data)
        print(url)
        with self.lock:
            answer = self.api.request('GET', url, fields)
            readdata = answer.read().decode('utf-8')
            retryTime = 0
            if 'Retry-After' in answer.headers:
                retryTime = answer.headers['Retry-After']
        if answer.status == 429:
            self.limit_fast.dec(retryTime)
            self.limit_slow.dec(retryTime)
            print("Limit exceeded received, slowing down")
        elif answer.status >= 500:
            print('Issues on the server side, hope for the best')
        if answer.status != 200:
            raise AnswerException('Error code returned by api: {err}'.format(err = answer.status), answer)
        elif not readdata:
            answer.status = 719
            raise AnswerException('No data received in answer', answer)
        return json.loads(readdata)

regToDlMap = defaultdict(Downloader)
def getDownloader(region):
    return regToDlMap[region]

