import paho.mqtt.client as mqtt
import ssl, time, json
import config
import blegateway

mqttCONFIG = config.get_config('mqtt')
ids = config.get_config('identifiers')

TOPIC = ids['location'] + "/" + ids['zone'] + "/"
print("Main Topic: " + TOPIC)
heartbeatTOPIC = 'heartbeat/' + ids['location'] + "/" + ids['zone']
print("Heartbeat Topic: " + heartbeatTOPIC)

DISCONNECTED = 0
CONNECTING = 1
CONNECTED = 2

if mqttCONFIG['ssl']:
    ROOT_CA = mqttCONFIG['ca']
    CLIENT_CERT = mqttCONFIG['cert']
    PRIVATE_KEY = mqttCONFIG['key']

def MQTT():
    isSSL = mqttCONFIG['ssl']
    if isSSL:
        ROOT_CA = mqttCONFIG['ca']
        CLIENT_CERT = mqttCONFIG['cert']
        PRIVATE_KEY = mqttCONFIG['key']
    state = DISCONNECTED
    global client
    client = mqtt.Client()
    if mqttCONFIG['user'] != None and \
        mqttCONFIG['password'] != None :
        client.username_pw_set(mqttCONFIG['user'], password=mqttCONFIG['password'])
    if isSSL == True:
        client.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    
    while state != CONNECTED:
        try:
            state = CONNECTING
            client.connect(mqttCONFIG['host'], mqttCONFIG['port'], 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            time.sleep(0.5)
    if state == CONNECTED:
            print('MQTT Client Connected')
    client.loop_start()

def heartbeat():
    client.publish( heartbeatTOPIC, json.dumps(blegateway.fill_heartbeat()), qos=0, retain=False )

def send_bt(bt_addr, message):
    client.publish( TOPIC + bt_addr, json.dumps(message), qos=0, retain=False )

def end():
    client.loop_stop()
    client.disconnect()