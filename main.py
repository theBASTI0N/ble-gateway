import time
from config import CONFIG as CONFIG
import sys
import time
from uptime import uptime
import datetime
import json
import paho.mqtt.client as mqtt
import ssl
import psutil

start = round(uptime())

if CONFIG.get('bleDevice') == 1:
    # Import Receiver for nRF module
    from beaconscanner import BeaconReceiver
else:
    # Import bluez scanner
    from beaconscanner import BeaconScanner

def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

DEVmac = str.upper(getMAC(CONFIG.get('interface')).translate({ord(':'): None}))

mFen = CONFIG.get('macFilterEn')
mF = CONFIG.get('macFilter')

TOPIC = CONFIG.get('topic1') + "/" + DEVmac + "/" + CONFIG.get('topic2') + "/"
print("Main Topic: " + TOPIC)
heartbeatTOPIC = CONFIG.get('topic1') + '/' + DEVmac + "/heartbeat"
print("Heartbeat Topic: " + heartbeatTOPIC)

DISCONNECTED = 0
CONNECTING = 1
CONNECTED = 2

if CONFIG.get('ssl'):
    ROOT_CA = CONFIG.get('ca')
    CLIENT_CERT = CONFIG.get('cert')
    PRIVATE_KEY = CONFIG.get('key')

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

def callback(bt_addr, rssi, packet, dec, smoothedRSSI):
    if mFen == True:
        for i in mF:
            if str.upper(i) == bt_addr:
                msg = dec
                msg['mac'] = bt_addr
                msg['edgeMAC'] = DEVmac
                msg['data'] = packet
                msg['rssi'] = rssi
                msg['rssiSmooth'] = smoothedRSSI
                ts = str(timestamp())
                ts = ts.translate({ord(' '): 'T'})
                ts = ts + "Z"
                msg['ts'] = ts
                msgJson = json.dumps(msg)
                client.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )
    else:
        msg = dec
        msg['mac'] = bt_addr
        msg['edgeMAC'] = DEVmac
        msg['data'] = packet
        msg['rssi'] = rssi
        msg['rssiSmooth'] = smoothedRSSI
        ts = str(timestamp())
        ts = ts.translate({ord(' '): 'T'})
        ts = ts + "Z"
        msg['ts'] = ts
        msgJson = json.dumps(msg)
        client.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )
   
def MQTT():
    isSSL = CONFIG.get('ssl')
    isUSR = CONFIG.get('usr')
    state = DISCONNECTED
    global client
    client = mqtt.Client()
    if isUSR == True:
        client.username_pw_set(CONFIG.get('user'), password=CONFIG.get('pass'))
    if isSSL == True:
        client.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    
    while state != CONNECTED:
        try:
            state = CONNECTING
            client.connect(CONFIG.get('host'), CONFIG.get('port'), 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            time.sleep(0.5)
    if state == CONNECTED:
            print('BLE MQTT Client Connected')
    client.loop_start()

def heartbeat():
    m = {}
    ts = str(timestamp())
    ts = ts.translate({ord(' '): 'T'})
    ts = ts + "Z"
    up = round(uptime()) - start
    cpu = psutil.cpu_percent()
    vMem = psutil.virtual_memory()
    m = {'ts' : ts,'edgeMAC' : DEVmac, 'type': CONFIG.get('gatewayType'),'uptime': up, 'cpu': cpu, 'totalMemory': vMem[0], 'availableMemory': vMem[1], 'percentUsedMemory': vMem[2], 'usedMemory': vMem[3], 'freeMemory': vMem[4]}
    msgJson = json.dumps(m)
    client.publish( heartbeatTOPIC, msgJson, qos=0, retain=False )

def main_loop():
    RSSIen = CONFIG.get('rssiEn')
    if (RSSIen):
        RSSI = CONFIG.get('rssi')
    else:
        RSSI = -999
    
    MQTT()
    global scanner
    if CONFIG.get('bleDevice') == 1:
        scanner = BeaconReceiver(callback, CONFIG.get('serialPort'), CONFIG.get('baudrate'), CONFIG.get('timeout'),\
                                rssiThreshold=RSSI,\
                                ruuvi=CONFIG.get('ruuvi'), ruuviPlus=CONFIG.get('ruuviPlus'),\
                                eddystone=CONFIG.get('eddystone'), ibeacon=CONFIG.get('ibeacon'), unknown=CONFIG.get('unknown'))
    else:
        scanner = BeaconScanner(callback, rssiThreshold=RSSI,\
                                ruuvi=CONFIG.get('ruuvi'), ruuviPlus=CONFIG.get('ruuviPlus'), \
                                eddystone=CONFIG.get('eddystone'), ibeacon=CONFIG.get('ibeacon'), unknown=CONFIG.get('unknown'))
    scanner.start()
    while True:
        if CONFIG.get('bleDevice') == 1:
            time.sleep(30)
            heartbeat()
        else:
            time.sleep(30)
            scanner._mon.toggle_scan(False)
            heartbeat()
            scanner._mon.toggle_scan(True)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        scanner.stop()
        client.loop_stop()
        client.disconnect()
        print("\nExiting application\n")
        sys.exit(0)
