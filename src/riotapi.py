import urllib3
import certifi
import json
import time

class RateLimit():
    def __init__(self, maxrate, seconds):
        self.maxrate = maxrate
        self.seconds = seconds
        self.timestamps = []
    
    def reset(self):
        self.timestamps.clear()
     
    def inc(self):
        if len(self.timestamps) < self.maxrate:
            self.timestamps.append(time.time())
            return
        elif self.timestamps[0]+self.seconds > time.time():
            print("Slowed to avoid over usage")
            time.sleep(self.timestamps[0]+self.seconds-time.time())
        self.timestamps.pop(0)
        self.timestamps.append(time.time())
        
    def cancel(self):
        pass
            
def createLimit(rate, seconds):
    return RateLimit(rate, seconds)
    
limit_fast = createLimit(10, 11.0)
limit_slow = createLimit(500, 610.0)

key = input("Input your api key ")
api = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)

class AnswerException(Exception):
    def __init__(self, msg, answer):
        Exception(msg)
        self.msg = msg
        self.answer = answer

def api_request(path, fields = None, **data):
    limit_fast.inc()
    limit_slow.inc()
    url = "https://global.api.pvp.net"
    data['api_key'] = key
    url += path
    url += '?' + '&'.join(str(arg) + '=' + str(data[arg]) for arg in data)
    print(url)
    answer = api.request('GET', url, fields)
    if answer.status == 429:
        print('Rate limit exceeded, check your key')
    if answer.status >= 500:
        print('')
    if answer.status != 200:
        raise AnswerException('Error code returned by api: {err}'.format(err = answer.status), answer)
    return json.loads(answer.data.decode('utf-8'))
