import lolstatic

import urllib3
import certifi
import json
import time
import sys
from optparse import OptionParser
from threading import Lock
from .RateLimit import RateLimit
from collections import defaultdict

parser = OptionParser()
parser.add_option("-f", "--failed", action="store_false", dest="ignoreFailedFiles",
                  default=True, help="Retry previously failed game ids")
parser.add_option("-k", default = False, action="store", dest="key", type="string", help="Retry previously failed game ids")
if not parser.parse_args(sys.argv)[0].key:
    print("To work correctly, the api needs to have a key")
    print("Start again with option -k <key>")
    sys.exit(-1)

class AnswerException(Exception):
    def __init__(self, msg, answer):
        Exception(msg)
        self.msg = msg
        self.answer = answer

class Downloader():
    """An API python-binding. Requests can be done via #api_request.
    The class automatically limits the usage of the API to conform to
    the restrictions of a production key: 3000 rq/10s and 180.000rq/10min
    """
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
            num_pools = 10,
            timeout = 5
        )
    

    def api_request(self, path, _reg = None, _fields = None, **data):
        """Makes an API request from the server, waiting if necessary to keep below the datacap.
        
        @param path: the API path of the requested data, e.g. "/api/lol/tr/v2.2/match/263959903".
        A leading slash is mandatory
        @param _reg: a specific server region to request the data from, e.g. 'na'
        @param _fields: the fields to forward to the raw HTTP-request. leading underscore to
        prevent conflicts with
        @param data: additional parameters for the request, e.g. includeTimeline=True
        @return: a parsed version of the received JSON response
        @raise AnswerException: when the HTTP status of the response is not 200.
        """
        if _reg is None:
            _reg = 'global'
        self.limit_fast.inc()
        self.limit_slow.inc()
        url = "https://{region}.api.pvp.net{path}".format(region = _reg, path = path)
        data['api_key'] = self.key
        url += '?' + '&'.join(str(arg) + '=' + str(data[arg]) for arg in data)
        print(url)
        with self.lock:
            answer = self.api.request('GET', url, fields = _fields)
            readdata = answer.data.decode('utf-8')
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
def getDownloader(region = None):
    """Gets the downloader for the specified region. If no region is given,
    returns the global downloader.
    """
    return regToDlMap[region]

