# ble2mqtt
BLE to MQTT application designed for use with linux PC's.

This application is designed to turn your linux PC into a functioning BLE
gateway. It creates a topic that is specific to each tag for ease of
subscribing and using the data.

# Tested on
The application has been tested on:
* RPI 3B+ : running Raspbian Buster
* RPI Zero W : running Raspbian Buster
* Dell Inspiron 7000 : running Fedora 31

# Installation

The below example if for a system based on Debian 10 which includes devices such as Raspberry Pi's.

```bash
# install libbluetooth, python3-pip, python3-bluez and git
sudo apt-get install python3-pip python3-bluez libbluetooth-dev git
# grant the python executable permission to access raw socket data
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
#install python modules
pip3 install beaconscanner uptime paho.mqtt psutil
#
cd ~/
#clone repository
git clone https://github.com/theBASTI0N/ble2mqtt.git && cd ble2mqtt
```

## Configuration
Edit the configuration file with your favourite editor.

The configuration file is located in the main directory being named config.py.
It contains all of the different configuration options.

Multiple configurations can be entered and called upon in the main application
on line 12. By adding for example "CONFIGhome"  instead of CONFIG with the name of your config.

Example:
```python

CONFIG = {
  "host" : "0.0.0.0",
  "ssl" : False,
  "ca" : '/cert/ca.pem', #if not using set to None
  "cert": '/cert/cert.pem', #if not using set to None
  "key": '/cert/cert.key', #if not using set to None
  "port" : 1883,
  "usr" : True,
  "user" : "",
  "pass" : "",
  "topic1" : "home",
  "topic2" : "beacon",
  "rssiEn" : False,
  "rssi" : -127,
  "macFilterEn" : False,
  "macFilter" : [ "c0bb722a568e", "dc3fd0bbcec2", "c467f2f9cf5a", "f7ac6ea886b1"],
  "tlm" : True,
  "ruuvi" : True,
  "unknown" : False,
  "interface": 'eth0' # RPI Ethernet = eth0   RPI Zero W = wlan0
}

```
* broker = The IP address of your MQTT broker.
* ssl = If wanting to use a SSL conenction to you broker.
* ca = Is the location of your CA certificate. Only imported if ssl is True
* cert = Is the location of your certificate. Only imported if ssl is True
* key = Is the location of your key. Only imported if ssl is True
* port = 1883 is the standard MQTT port, if using SSL 8883 is standard
* usr = Enable this if your broker requires a username and password to connect
* mqttuser = Username required for broker conenction
* mqttpass = Password required for broker connection
* topic1 = can be used to identifiy each gateway further. For example "kitchen"
* topic2 = used to publish ble Data
* rssiEn = Enable if RSSI filtering is wanted
* rssi = Set the RSSI filter for example -40 would be almost touching the board
* macFilterEn = Enable this if you want to only send data on specific BLE beacons
* macFilter = The list of ble beacons to send data for
* tlm = Set to true to enable the forwarding of TLM data
* ruuvi = Set to true to enable the forwarding of Ruuvi data
* unknnown= Set to true to enable the forwarding of unknown data
* interface = Set to the interface you want to set as the identifier of the device. Eg mac address of eth0

## Service

To enable the application as a service so it will run at boot. The following can be followed:

```bash
#move to service director
cd ~/ble2mqtt/service
#copy the service file to the correct location
sudo cp ble2mqtt.service /etc/systemd/system/
#enable the service to start on boot
sudo systemctl enable ble2mqtt
#start the service
sudo systemctl start ble2mqtt
#check it is running. If active all is working
sudo systemctl status ble2mqtt
```

# Visualisation

To visualise the data the following has been tested and is required. Versions may differ depending on system you are using.
* MQTT broker (mosquitto on a RPI)
* Node-RED
* Grafana (I am using v6.3.6)
* InfluxDB (I am using V1.7.8)

## Used Software

I created 4 databases in influxDB. Those are:
* unknownBeacons - This is optional, no need to create if not collecting the data.
* TLM
* Ruuvi
* linux - This is for heartbeat data and is optional

## Node-RED Flows

The Example can be found in the Node-RED Flows folder.

## Grafana

Grafana Examples can be found in the grafana folder.