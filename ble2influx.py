from influxdb import InfluxDBClient
import json
import config
import blegateway

influxCONFIG = config.get_config('influx')
ids = config.get_config('identifiers')

def INFLUX():
    if influxCONFIG['user'] == None:
        influxCONFIG['user'] = 'root'
    if influxCONFIG['password'] == None:
        influxCONFIG['password'] = 'root'
    global client
    client = InfluxDBClient(influxCONFIG['host'], influxCONFIG['port'], \
        influxCONFIG['user'], influxCONFIG['password'], influxCONFIG['database'])
    
    dbs = client.get_list_database()
    if influxCONFIG['database'] in dbs:
        pass
    else:
        client.create_database(influxCONFIG['database'])
    client.switch_database(influxCONFIG['database'])

def heartbeat():
    temp = blegateway.fill_heartbeat()
    msg = []
    _msg = {
            "measurement": 'heartbeat_measurements',
            "tags": {
                "edgeMac": temp['edgeMAC'],
                "edgeType": temp['type']
            },
            "fields": {
                "edgeMAC": temp['edgeMAC'],
                "edgeType": temp['type'],
                "uptime": temp['uptime'],
                "cpu": temp['cpu'],
                "totalMemory": temp['totalMemory'],
                "availableMemory": temp['availableMemory'],
                "percentUsedMemory": temp['percentUsedMemory'],
                "usedMemory": temp['usedMemory'],
                "freeMemory": temp['freeMemory'],
                "location": temp['location'],
                "zone": temp['zone'],
            }
        }
    
    msg.append(_msg)
    client.write_points(msg)

def send_bt(bt_addr, message):
    if message['dataFormat'] == 10:
        mesurement = 'uid_measurements'
    elif message['dataFormat'] == 11:
        mesurement = 'url_measurements'
    elif message['dataFormat'] == 12:
        mesurement = 'tlm_measurements'
    elif message['dataFormat'] == 13:
        mesurement = 'etlm_measurements'
    elif message['dataFormat'] == 14:
        mesurement = 'eid_measurements'
    elif message['dataFormat'] == 20:
        mesurement = 'ibeacon_measurements'
    elif message['dataFormat'] == 3 or message['dataFormat'] == 5:
        mesurement = 'ruuvi_measurements'
    else:
        mesurement = 'unknown_measurements'
    
    tags = {"mac": bt_addr, "edgeMAC": message['edgeMAC']}
    items = {}

    if 'name' in message:
        tags['name'] = message['name']

    for i in message:
        if 'data' in i or 'ts' in i:
            pass
        else:
            items[i] = message[i]
    
    msg = []
    _msg = {
            "measurement": mesurement,
            "tags": tags,
            "fields": items
        }
    
    msg.append(_msg)
    client.write_points(msg)