# BLE Gateway
BLE Gateway is an application designed for use with linux PC's.

This application is designed to turn your linux based PC into a functioning BLE gateway.

It supports MQTT, HTTP and influxDB endpoints and allows multiple to be used at one time.

It relies on 3 other ptyhon module to work correctly:
* pybluez - 0.22
* beacondecoder - 0.6.2
* beaconscanner - 1.2.4

Also supports external nRF52832 module.

# Tested on
The application has been tested on:
* RPI 3B+ : running Raspbian Buster
* RPI Zero W : running Raspbian Buster
* Dell Inspiron 7000 : running Fedora 31 and Ubuntu 20

# External BLE module

To use an external ble module the nrf module in beaconscanner is wanting to receive the following information:
mac address, ble packet, rssi

https://github.com/ruuvi/ruuvi.gateway_nrf.c

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

The below example is for a system based on Debian 10 which includes devices such as Raspberry Pi's or Ubuntu based OS's.

```bash
# install libbluetooth, python3-pip, python3-bluez and git
sudo apt-get install python3-pip python3-bluez libbluetooth-dev git
# grant the python executable permission to access raw socket data
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
#install python modules
pip3 install beaconscanner uptime paho-mqtt psutil influxdb
#
cd ~/
#clone repository
git clone https://github.com/theBASTI0N/ble-gateway.git && cd ble-gateway
```

## Configuration
Edit the configuration file with your favourite editor.

The configuration file is located in the config directory being named blegateway.json.
It contains all of the different configuration options.

```
* bleDevice = Contains the information on the ble device that will be used.
** bleDevice = 0 for builtin device, 1 for serial device
* filters = Allows multiple filters to be applied.
** eddystone = Allows eddystone TLM device to be seen.
** ibeacon = Allows ibeacon tags to be seen.
** ruuvi = Allows RuuviTag beacons to be seen.
** ruuviPlus = Allows enhanced ruuvi decoding to occur.
** rssiThreshold = Enables the RSSI threshold
** rssi = If above enabled only device with q stronger RSSI will be seen.
* identifiers = Allows ids to be given to multiple gateways.
** interface = Select which network interface to use to get the mac.
** location = Overarching location eg. Head Office
** zone = More specific location eg. Board Room
** gatewayType = Used for grouping track of heartbeat data of similar devices.
* endpoints = Allows the toggling of different endpoint types. Currently MQTT, HTTP and InfluxDB are supported.
* mqtt = Allows the configuration of a MQTT endpoint
* http = Allows the configuration of a http endpoint
* influx = Allows the configuration of a influxDB endpoint

```

## Service

To enable the application as a service so it will run at boot. The following can be followed:

```bash
#move to service director
cd ~/ble-gateway/service
#copy the service file to the correct location
sudo cp blegateway.service /etc/systemd/system/
#enable the service to start on boot
sudo systemctl enable blegateway
#start the service
sudo systemctl start blegateway
#check it is running. If active all is working
sudo systemctl status blegateway
```

NOTE: This has been designed ot run on a Raspberry Pi.

# RuuviCollector

I have designed this application to work with:
https://github.com/Scrin/RuuviCollector

This is why the readings go into the influxDB database ruuvi when using either MQTT/node-red and influxDB endpoints by default.

# Visualisation

To visualise the data the following has been tested and is required. Versions may differ depending on system you are using.
* MQTT broker
* Node-RED
* Grafana
* InfluxDB

## Node-RED Flows

The Example can be found in the Node-RED Flows folder. It will pass MQTT messages to influxDB.

## Grafana

Grafana Examples can be found in the grafana folder.
