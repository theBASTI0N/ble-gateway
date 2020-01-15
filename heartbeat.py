import time
import sys
import time
from uptime import uptime
import datetime
import json
import paho.mqtt.client as mqtt
import ssl
from config import CONFIG as CONFIG

def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]
DEVmac = getMAC(CONFIG.get('interface'))
DEVmac = str.upper(DEVmac.translate({ord(':'): None}))

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

def heartbeat():
    print("Heartbeat Started")
    while True:
        try:
            m = {}
            ts = str(timestamp())
            ts = ts.translate({ord(' '): 'T'})
            ts = ts + "Z"
            up = round(uptime())
            m = {'ts' : ts,'edgeMAC' : DEVmac,'uptime': up}
            msgJson = json.dumps(m)
            mqttc.publish( CONFIG.get('topic1') + "/" + DEVmac + "/heartbeat", msgJson, qos=0, retain=False )
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
    heartbeatMQTT()
    heartbeat()

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        clientH.loop_stop()
        clientH.disconnect()
        print("\nExiting application\n")
        sys.exit(0)