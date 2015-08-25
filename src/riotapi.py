import urllib3
import certifi
import json

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
