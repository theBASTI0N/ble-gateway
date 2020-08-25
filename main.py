import time
import sys
import json
import blegateway
import config

if config.get_config('bleDevice')['bleDevice'] == 1:
    # Import Receiver for nRF module
    from beaconscanner import BeaconReceiver
else:
    # Import bluez scanner
    from beaconscanner import BeaconScanner

mqttEnabled = config.get_config('endpoints')['mqttEnabled']
httpEnabled = config.get_config('endpoints')['httpEnabled']
influxEnabled = config.get_config('endpoints')['influxEnabled']

if mqttEnabled:
    import ble2mqtt
if httpEnabled:
    import ble2http
if influxEnabled:
    import ble2influx

try:
    names = config.get_config('names')
except:
    namesEnabled = False
else:
    namesEnabled = True

mFen = config.get_config('filters')['macFilterEnabled']
if mFen:
    mF = config.get_config('filters')['macFilter']

def callback(bt_addr, rssi, packet, dec, smoothedRSSI):
    if namesEnabled:
        if bt_addr in names:
            name = names[bt_addr]
        else:
            name = None
    else:
        name = None
    if mFen == True:
        for i in mF:
            if str.upper(i) == bt_addr:
                if mqttEnabled:
                    ble2mqtt.send_bt(bt_addr, blegateway.ble_message\
                        (bt_addr, rssi, packet, dec, smoothedRSSI, name))
                if influxEnabled:
                    ble2influx.send_bt(bt_addr, blegateway.ble_message\
                        (bt_addr, rssi, packet, dec, smoothedRSSI, name))
                if httpEnabled:
                    ble2http.send_bt(bt_addr, blegateway.ble_message\
                        (bt_addr, rssi, packet, dec, smoothedRSSI, name))
    else:
        if mqttEnabled:
            ble2mqtt.send_bt(bt_addr, blegateway.ble_message\
                (bt_addr, rssi, packet, dec, smoothedRSSI, name))
        if influxEnabled:
            ble2influx.send_bt(bt_addr, blegateway.ble_message\
                (bt_addr, rssi, packet, dec, smoothedRSSI, name))
        if httpEnabled:
            ble2http.send_bt(bt_addr, blegateway.ble_message\
                (bt_addr, rssi, packet, dec, smoothedRSSI, name))
   

def main_loop():
    RSSIen = config.get_config('filters')['rssiThreshold']
    if (RSSIen):
        RSSI = config.get_config('filters')['rssi']
    else:
        RSSI = -999
    if mqttEnabled:
        ble2mqtt.MQTT()
    if influxEnabled:
        ble2influx.INFLUX()
    global scanner
    f = config.get_config('filters')
    if config.get_config('bleDevice')['bleDevice'] == 1:
        scanner = BeaconReceiver(callback, config.get_config('bleDevice')['serialPort'], \
                                config.get_config('bleDevice')['baudrate'], \
                                config.get_config('bleDevice')['timeout'],\
                                rssiThreshold=RSSI,\
                                ruuvi=f['ruuvi'], ruuviPlus=f['ruuviPlus'], \
                                eddystone=f['eddystone'], ibeacon=f['ibeacon'], unknown=f['unknown'])
    else:
        scanner = BeaconScanner(callback, rssiThreshold=RSSI,\
                                ruuvi=f['ruuvi'], ruuviPlus=f['ruuviPlus'], \
                                eddystone=f['eddystone'], ibeacon=f['ibeacon'], unknown=f['unknown'])
    scanner.start()
    while True:
        if config.get_config('bleDevice')['bleDevice'] == 1:
            time.sleep(30)
            if mqttEnabled:
                ble2mqtt.heartbeat()
            if influxEnabled:
                ble2influx.heartbeat()
            if httpEnabled:
                ble2http.heartbeat()
        else:
            time.sleep(30)
            scanner._mon.toggle_scan(False)
            if mqttEnabled:
                ble2mqtt.heartbeat()
            if influxEnabled:
                ble2influx.heartbeat()
            if httpEnabled:
                ble2http.heartbeat()
            scanner._mon.toggle_scan(True)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        scanner.stop()
        if mqttEnabled:
            ble2mqtt.end()
        print("\nExiting application\n")
        sys.exit(0)
