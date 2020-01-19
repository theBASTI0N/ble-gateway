# ble2mqtt
BLE to MQTT application designed for use with linux PC's.

This application is designed to turn your linux PC into a functioning BLE
gateway. It creates a topic that is specific to each tag for ease of
subscribing and using the data.

It relies on 3 other ptyhon module to work correctly:
* pybluez - 0.22
* beacondecoder - 0.4
* beaconscanner - 1.1.0

Also supports external nRF52832 module.

# Tested on
The application has been tested on:
* RPI 3B+ : running Raspbian Buster
* RPI Zero W : running Raspbian Buster
* Dell Inspiron 7000 : running Fedora 31

# External BLE module

To use an external ble module the nrf module in beaconscanner is wanting to receive the following information:
channel, rssi, mac address, ble packet

https://github.com/theBASTI0N/nrf52832_scanner

The above repository can be used to flash a nRF52832 module to provide this data.

This has been tested on the following ble module:
Ruuvitag
Raytac MDBT42Q-U512KV2

## RPI

The RPI's built in serial connections cannot be used out of the box as it is used to connect to the RPI's console over serial. To enable the use of the serial pin the following needs to be done:

```bash
  sudo raspi-config 
```

Select 'Interfacing Options'
Select 'Serial'
Select 'No'
Select ' Yes'

Then reboot

You will now have /dev/ttyS0 listed in the devices. Connect your module to the follwing pins on your RPI:
* Pin 8 - TX
* Pin 10 - RX

NOTE: If you do not want to disable to serial console an external USB to serial adapter can be used.

## Onion Omega

On Onion Omega devices TX1 and RX1 pins can be used to connect UART devices.

The serial device that corresponds to these pins is /dev/ttyS1

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
  "host" : "0.0.0.0", # This can also be a DNS entry
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
  "interface": 'eth0', # RPI Ethernet = eth0   RPI Zero W = wlan0
  "bleDevice" : 0,  #0 = built in bluez device, 1 = serial device
  "serialPort" : '/dev/ttyS0',  # '/dev/ttyS0' most liekly on RPI, '/dev/ttyS1' most liekly on Onion Omega 2+
  "baudrate" : 115200,
  "timeout" : 1
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
* bleDevice = 0 built in bluez device, 1 is an externals erial device
* serialPortt = The port of the external BLE module
* baudrate = The baudrate of the external BLE module
* timeout = The timeout of the external BLE module

The below is an example of importing a specific config in main.py:
```python
from config import CONFIGhome as CONFIG
```

This assumes your config file is like:

```python
CONFIG = {
  "details" : 'go here'
}

CONFIGhome = {
  "details" : 'of second config go here'
}

```

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