import requests
import json
import config
import blegateway

httpCONFIG = config.get_config('http')
header = {'Content-type': 'application/json'}

def heartbeat():
    requests.post(httpCONFIG['host'],
                         data=json.dumps(blegateway.fill_heartbeat()).encode('utf8'),
                         headers=header)

def send_bt(bt_addr, message):
    requests.post(httpCONFIG['host'], data=json.dumps(message).encode('utf8'), headers=header)
