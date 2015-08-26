import urllib3
import certifi
import json
import time
from threading import Lock

'''
This class restricts the number of api queries in a short time frame to a certain amount thus avoiding unecessary error messages and annoying error handling.
It is not thread safe, which should not be a problem since we only have one downloading thread anyways.
'''
class RateLimit():
    def __init__(self, maxrate, seconds):
        self.maxrate = maxrate
        self.rate = maxrate
        self.minseconds = seconds
        self.seconds = seconds
        self.timestamps = []
        self.lock = Lock()
    
    def __enter__(self):
        self.lock.acquire()
    
    def __exit(self, type_t, value, traceback):
        self.lock.release()
    
    def reset(self):
        self.timestamps.clear()
    '''
    This method should be called whenever someone tries to access the protected resource
    It blocks when too many callers tried to access in same timeframe.
    Every 
    '''
    def inc(self):
        with self:
            while self.timestamps[0]+self.seconds > time.time() or len(self.timestamps) >= self.rate:
                print("Slowed to avoid over usage")
                time.sleep(self.timestamps[0]+self.seconds-time.time())
                self.timestamps.pop(0)
            self.timestamps.append(time.time())
    '''
    This method decreases the rate limit according to the parameters for a while.
    '''
    def dec(self):
        with self:
            pass
        
    def cancel(self):
        pass
            
def createLimit(rate, seconds):
    return RateLimit(rate, seconds)
    
limit_fast = createLimit(3000, 12.0)
limit_slow = createLimit(180000, 620.0)

key = input("Input your api key ").strip()# Aks for a key to avoid storing it
api = urllib3.PoolManager(          # https connector
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)

class AnswerException(Exception):
    def __init__(self, msg, answer):
        Exception(msg)
        self.msg = msg
        self.answer = answer

def api_request(region, path, fields = None, **data):
    limit_fast.inc()
    limit_slow.inc()
    url = "https://{region}.api.pvp.net{path}".format(**locals())
    data['api_key'] = key
    url += '?' + '&'.join(str(arg) + '=' + str(data[arg]) for arg in data)
    print(url)
    answer = api.request('GET', url, fields)
    if answer.status == 429:
        print('Rate limit exceeded, check your key')
    if answer.status >= 500:
        print('Issues on the server side, hope for the best')
    if answer.status != 200:
        raise AnswerException('Error code returned by api: {err}'.format(err = answer.status), answer)
    return json.loads(answer.data.decode('utf-8'))
