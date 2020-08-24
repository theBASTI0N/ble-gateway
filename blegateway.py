import datetime
from uptime import uptime
import psutil
import config

start = round(uptime())

def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

DEVmac = str.upper(getMAC(config.get_config('identifiers')['interface']).translate({ord(':'): None}))

def gateway_mac():
    return DEVmac

def timestamp():
    t = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    t = str(t)
    t = t.translate({ord(' '): 'T'})
    return t + 'Z'
    
def fill_heartbeat():
    up = round(uptime()) - start
    cpu = psutil.cpu_percent()
    vMem = psutil.virtual_memory()
    return {'ts': timestamp(), 'edgeMAC': DEVmac, 'type': config.get_config('identifiers')['gatewayType'], \
        'uptime': up, 'cpu': cpu, 'totalMemory': vMem[0], 'availableMemory': vMem[1], \
        'percentUsedMemory': vMem[2], 'usedMemory': vMem[3], 'freeMemory': vMem[4], \
        'location': config.get_config('identifiers')['location'], 'zone': config.get_config('identifiers')['zone']}

def ble_message(bt_addr, rssi, packet, decoded, smoothedRSSI):
    msg = decoded
    msg['mac'] = bt_addr
    msg['edgeMAC'] = gateway_mac()
    msg['data'] = packet
    msg['rssi'] = rssi
    msg['rssiSmooth'] = smoothedRSSI
    msg['ts'] = timestamp()
    msg['location'] = config.get_config('identifiers')['location']
    msg['zone'] = config.get_config('identifiers')['zone']
    return msg
