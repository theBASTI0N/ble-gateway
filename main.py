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
DEVmac = getMAC(CONFIG.get('interface'))
DEVmac = str.upper(DEVmac.translate({ord(':'): None}))

mFen = CONFIG.get('macFilterEn')
mF = CONFIG.get('macFilter')
RSSIen = CONFIG.get('rssiEn')
RSSI = CONFIG.get('rssi')
TLM = CONFIG.get('tlm')
RUUVI = CONFIG.get('ruuvi')
UNKNOWN = CONFIG.get('unknown')

TOPIC = CONFIG.get('topic1') + "/" + DEVmac + "/" + CONFIG.get('topic2') + "/"
print("Main Topic: " + TOPIC)

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
    if (RUUVI and dec['f'] == 3) or (RUUVI and dec['f'] == 5) or (TLM and dec['f'] == 1) or (UNKNOWN and dec['f'] == 0): 
        if RSSIen:
            if rssi >= RSSI :
                if mFen == True:
                    for i in mF:
                        if str.upper(i) == bt_addr:
                            msg = dec
                            msg['Mac'] = bt_addr
                            msg['edgeMAC'] = DEVmac
                            msg['data'] = packet
                            msg['rssi'] = rssi
                            msg['rssiSmooth'] = smoothedRSSI
                            ts = str(timestamp())
                            ts = ts.translate({ord(' '): 'T'})
                            ts = ts + "Z"
                            msg['ts'] = ts
                            msgJson = json.dumps(msg)
                            clientBLE.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )
                else:
                    msg = dec
                    msg['Mac'] = bt_addr
                    msg['edgeMAC'] = DEVmac
                    msg['data'] = packet
                    msg['rssi'] = rssi
                    msg['rssiSmooth'] = smoothedRSSI
                    ts = str(timestamp())
                    ts = ts.translate({ord(' '): 'T'})
                    ts = ts + "Z"
                    msg['ts'] = ts
                    msgJson = json.dumps(msg)
                    clientBLE.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )
        else:
            if mFen == True:
                    for i in mF:
                        if str.upper(i) == bt_addr:
                            msg = dec
                            msg['Mac'] = bt_addr
                            msg['edgeMAC'] = DEVmac
                            msg['data'] = packet
                            msg['rssi'] = rssi
                            msg['rssiSmooth'] = smoothedRSSI
                            ts = str(timestamp())
                            ts = ts.translate({ord(' '): 'T'})
                            ts = ts + "Z"
                            msg['ts'] = ts
                            msgJson = json.dumps(msg)
                            clientBLE.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )
            else:
                msg = dec
                if channel != 0:
                    msg['channel'] = channel
                msg['Mac'] = bt_addr
                msg['edgeMAC'] = DEVmac
                msg['data'] = packet
                msg['rssi'] = rssi
                msg['rssiSmooth'] = smoothedRSSI
                ts = str(timestamp())
                ts = ts.translate({ord(' '): 'T'})
                ts = ts + "Z"
                msg['ts'] = ts
                msgJson = json.dumps(msg)
                clientBLE.publish( TOPIC + bt_addr, msgJson, qos=0, retain=False )

def bleMQTT():
    isSSL = CONFIG.get('ssl')
    isUSR = CONFIG.get('usr')
    state = DISCONNECTED
    global clientBLE
    clientBLE = mqtt.Client()
    if isUSR == True:
        clientBLE.username_pw_set(CONFIG.get('user'), password=CONFIG.get('pass'))
    if isSSL == True:
        clientBLE.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    
    while state != CONNECTED:
        try:
            state = CONNECTING
            clientBLE.connect(CONFIG.get('host'), CONFIG.get('port'), 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            time.sleep(0.5)
    if state == CONNECTED:
            print('BLE MQTT Client Connected')
    clientBLE.loop_start()

def heartbeat():
    print("Heartbeat Started")
    while True:
        try:
            m = {}
            ts = str(timestamp())
            ts = ts.translate({ord(' '): 'T'})
            ts = ts + "Z"
            up = round(uptime())
            cpu = psutil.cpu_percent()
            vMem = psutil.virtual_memory()
            m = {'ts' : ts,'edgeMAC' : DEVmac,'uptime': up, 'cpu': cpu, 'totalMemory': vMem[0], 'availableMemory': vMem[1], 'percentUsedMemory': vMem[2], 'usedMemory': vMem[3], 'freeMemory': vMem[4]}
            msgJson = json.dumps(m)
            clientH.publish( CONFIG.get('topic1') + "/linux/" + DEVmac + "/heartbeat", msgJson, qos=0, retain=False )
            time.sleep(30)
        except:
            pass

def heartbeatMQTT():
    isSSL = CONFIG.get('ssl')
    isUSR = CONFIG.get('usr')
    state = DISCONNECTED
    global clientH
    clientH = mqtt.Client()
    if isUSR == True:
        clientH.username_pw_set(CONFIG.get('user'), password=CONFIG.get('pass'))
    if isSSL == True:
        clientH.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    while state != CONNECTED:
        try:
            state = CONNECTING
            clientH.connect(CONFIG.get('host'), CONFIG.get('port'), 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            time.sleep(0.5)
    if state == CONNECTED:
            print('Heartbeat MQTT Client Connected')
    clientH.loop_start()

def main_loop():
    bleMQTT()
    global scanner
    if CONFIG.get('bleDevice') == 1:
        scanner = BeaconReceiver(callback, CONFIG.get('serialPort'), CONFIG.get('baudrate'), CONFIG.get('timeout'))
    else:
        scanner = BeaconScanner(callback)
    scanner.start()
    heartbeatMQTT()
    heartbeat()

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        scanner.stop()
        clientBLE.loop_stop()
        clientBLE.disconnect()
        clientH.loop_stop()
        clientH.disconnect()
        print("\nExiting application\n")
        sys.exit(0)
