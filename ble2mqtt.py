import paho.mqtt.client as mqtt
import ssl, time, json
import config
import ble2

TOPIC = config.get_config('identifiers')['location'] + "/" + config.get_config('identifiers')['zone'] + "/"
print("Main Topic: " + TOPIC)
heartbeatTOPIC = 'heartbeat/' + config.get_config('identifiers')['location'] + "/" + config.get_config('identifiers')['zone']
print("Heartbeat Topic: " + heartbeatTOPIC)

DISCONNECTED = 0
CONNECTING = 1
CONNECTED = 2

if config.get_config('mqtt')['ssl']:
    ROOT_CA = config.get_config('mqtt')['ca']
    CLIENT_CERT = config.get_config('mqtt')['cert']
    PRIVATE_KEY = config.get_config('mqtt')['key']

def MQTT():
    isSSL = config.get_config('mqtt')['ssl']
    if isSSL:
        ROOT_CA = config.get_config('mqtt')['ca']
        CLIENT_CERT = config.get_config('mqtt')['cert']
        PRIVATE_KEY = config.get_config('mqtt')['key']
    state = DISCONNECTED
    global client
    client = mqtt.Client()
    if config.get_config('mqtt')['user'] != None and \
        config.get_config('mqtt')['password'] != None :
        client.username_pw_set(config.get_config('mqtt')['user'], password=config.get_config('mqtt')['password'])
    if isSSL == True:
        client.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    
    while state != CONNECTED:
        try:
            state = CONNECTING
            client.connect(config.get_config('mqtt')['host'], config.get_config('mqtt')['port'], 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            time.sleep(0.5)
    if state == CONNECTED:
            print('MQTT Client Connected')
    client.loop_start()

def heartbeat():
    client.publish( heartbeatTOPIC, json.dumps(ble2.fill_heartbeat()), qos=0, retain=False )

def send_bt(bt_addr, message):
    client.publish( TOPIC + bt_addr, message, qos=0, retain=False )

def end():
    client.loop_stop()
    client.disconnect()