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
pip3 install beaconscanner
#
cd ~/
#clone repository
git clone https://github.com/theBASTI0N/ble2mqtt.git && cd ble2mqtt
```

## Configuration

The configuration file is located in the main directory being named config.py.
It contains all of the different configuration options.

Multiple configurations can be entered and called upon in the main application
on line 12. By replacing "CONFIGhome" with the name of your config.

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
sudo systemctl enable ble2mqtt
```

# Visualisation

Software needed:
* MQTT broker (mosquitto on a RPI)
* Node-RED
* Grafana (I am using v6.3.6)
* InfluxDB (I am using V1.7.8)

## Used Software

I created 3 databases in influxDB. Those are:
* unknownBeacons
* TLM
* Ruuvi

## Node-RED Flows

The below flows will pass all received data into their corresponding databases.

```json

[{"id":"e184de2d.f9883","type":"tab","label":"BLE2MQTT2INFLUX","disabled":false,"info":""},{"id":"211dbd92.7c49e2","type":"function","z":"e184de2d.f9883","name":"TLM","func":"var tokens  = msg.topic.split(\"/\");\nmsg.topic   =tokens[3];       //get device  name from topic  level 3 /v1.6/devices/tokens[3]\nvar dest    = tokens[tokens.length-1];\ninputjson   =JSON.parse(msg.payload);\nvar _fields = {};\nfor(var item in inputjson){\n    if (item.includes('Data') || item.includes(\"ts\")){}\n    else\n    {\n    _fields[item] = inputjson[item];}\n}\n\nvar tags = {\n            Mac: inputjson['Mac'],\n            esgeMAC: inputjson['edgeMAC']\n        } ;\n\nmsg.payload = [ \n    {        //device name as measurement\n        measurement: \"TLM_Data\",\n        tags,\n        fields: _fields\n    }\n    ];\n    \nreturn msg;","outputs":1,"noerr":0,"x":870,"y":160,"wires":[["8acb47f4.5155d8"]]},{"id":"4b425dc7.05fe24","type":"switch","z":"e184de2d.f9883","name":"","property":"payload.f","propertyType":"msg","rules":[{"t":"eq","v":"0","vt":"str"},{"t":"eq","v":"1","vt":"str"},{"t":"eq","v":"3","vt":"str"},{"t":"eq","v":"5","vt":"str"}],"checkall":"true","repair":false,"outputs":4,"x":505,"y":156,"wires":[["4672a641.6e33b8"],["42b4cd3a.5b1b64"],["c37f1e0d.fe8bf"],["c37f1e0d.fe8bf"]]},{"id":"953817ff.3a4d08","type":"json","z":"e184de2d.f9883","name":"","property":"payload","action":"","pretty":false,"x":335,"y":156,"wires":[["4b425dc7.05fe24"]]},{"id":"42b4cd3a.5b1b64","type":"json","z":"e184de2d.f9883","name":"","property":"payload","action":"","pretty":false,"x":710,"y":160,"wires":[["211dbd92.7c49e2"]]},{"id":"fe884652.0b6638","type":"function","z":"e184de2d.f9883","name":"Ruuvi","func":"var tokens  = msg.topic.split(\"/\");\nmsg.topic   =tokens[3];       //get device  name from topic  level 3 /v1.6/devices/tokens[3]\nvar dest    = tokens[tokens.length-1];\ninputjson   =JSON.parse(msg.payload);\nvar _fields = {};\nfor(var item in inputjson){\n    if (item.includes('Data') || item.includes(\"ts\")){}\n    else\n    {\n    _fields[item] = inputjson[item];}\n}\n\nvar tags = {\n            Mac: inputjson['Mac'],\n            edgeMAC: inputjson['edgeMAC']\n        } ;\n\nmsg.payload = [ \n    {\n        measurement: \"Ruuvi_Data\" ,\n        tags,     //device name as measurement\n        fields: _fields\n    },\n    ];\n    \nreturn msg;","outputs":1,"noerr":0,"x":875,"y":196,"wires":[["955726d0.7886b8"]]},{"id":"c37f1e0d.fe8bf","type":"json","z":"e184de2d.f9883","name":"","property":"payload","action":"","pretty":false,"x":715,"y":196,"wires":[["fe884652.0b6638"]]},{"id":"14d5955a.a27f1b","type":"mqtt in","z":"e184de2d.f9883","name":"","topic":"home/+/beacon/#","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":125,"y":156,"wires":[["24bbe690.ee84fa","953817ff.3a4d08"]]},{"id":"24bbe690.ee84fa","type":"debug","z":"e184de2d.f9883","name":"","active":false,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","x":150,"y":200,"wires":[]},{"id":"429320e6.b803","type":"comment","z":"e184de2d.f9883","name":"MQTT2Influx","info":"","x":125,"y":56,"wires":[]},{"id":"4672a641.6e33b8","type":"json","z":"e184de2d.f9883","name":"","property":"payload","action":"","pretty":false,"x":705,"y":116,"wires":[["911eb92c.6d5d18"]]},{"id":"911eb92c.6d5d18","type":"function","z":"e184de2d.f9883","name":"Unknown","func":"var tokens  = msg.topic.split(\"/\");\nmsg.topic   =tokens[3];       //get device  name from topic  level 3 /v1.6/devices/tokens[3]\nvar dest    = tokens[tokens.length-1];\ninputjson   =JSON.parse(msg.payload);\nvar _fields = {};\nfor(var item in inputjson){\n    if (item.includes('Data') || item.includes(\"ts\")){}\n    else\n    {\n    _fields[item] = inputjson[item];}\n}\n\nvar tags = {\n            Mac: inputjson['Mac'],\n            esgeMAC: inputjson['edgeMAC']\n        } ;\n\nmsg.payload = [ \n    {        //device name as measurement\n        measurement: \"Unknown_Beacon\",\n        tags,\n        fields: _fields\n    }\n    ];\n    \nreturn msg;","outputs":1,"noerr":0,"x":875,"y":116,"wires":[["709f3350.75f02c"]]},{"id":"955726d0.7886b8","type":"influxdb batch","z":"e184de2d.f9883","influxdb":"c598a3ff.40fa6","precision":"","retentionPolicy":"","name":"","x":1005,"y":196,"wires":[]},{"id":"8acb47f4.5155d8","type":"influxdb batch","z":"e184de2d.f9883","influxdb":"52d8d338.02671c","precision":"","retentionPolicy":"","name":"TLM","x":1025,"y":156,"wires":[]},{"id":"709f3350.75f02c","type":"influxdb batch","z":"e184de2d.f9883","influxdb":"6e88ee26.41e24","precision":"","retentionPolicy":"","name":"","x":1105,"y":96,"wires":[]},{"id":"3369677a.74aeb8","type":"tab","label":"Pycom Board Health","disabled":false,"info":""},{"id":"d5f9617.9a83aa","type":"mqtt in","z":"3369677a.74aeb8","name":"","topic":"home/240AC4024A6C/beacon/device/heartbeat","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":300,"y":140,"wires":[["838beac4.749028"]]},{"id":"159c5a5b.88b086","type":"mqtt in","z":"3369677a.74aeb8","name":"","topic":"home/240AC400DE4C/beacon/device/heartbeat","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":302,"y":108,"wires":[["838beac4.749028"]]},{"id":"57bb169f.99f248","type":"mqtt in","z":"3369677a.74aeb8","name":"","topic":"home/3C71BF877D24/beacon/device/heartbeat","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":301,"y":223,"wires":[[]]},{"id":"efa28f5b.1c22a","type":"comment","z":"3369677a.74aeb8","name":"SiPy's","info":"","x":160,"y":79,"wires":[]},{"id":"fd6e9c8a.f1445","type":"function","z":"3369677a.74aeb8","name":"","func":"var tokens  = msg.topic.split(\"/\");\nmsg.topic   =tokens[3];       //get device  name from topic  level 3 /v1.6/devices/tokens[3]\nvar dest    = tokens[tokens.length-1];\ninputjson   =JSON.parse(msg.payload);\nvar _fields = {};\nfor(var item in inputjson){\n    if (item.includes('Data') || item.includes(\"ts\")){}\n    else\n    {\n    _fields[item] = inputjson[item];}\n}\n\nvar tags = {\n            edgeMac: inputjson['edgeMAC'],\n            boardType: inputjson['board']\n        } ;\n\nmsg.payload = [ \n    {\n        measurement: \"PycomHealth\",\n        tags,     //device name as measurement\n        fields: _fields\n    },\n    ];\n    \nreturn msg;","outputs":1,"noerr":0,"x":670,"y":340,"wires":[["29862159.36d95e"]]},{"id":"78d8d0d4.b0bbe","type":"mqtt in","z":"3369677a.74aeb8","name":"","topic":"home/3C71BF877D48/beacon/device/heartbeat","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":299,"y":256,"wires":[[]]},{"id":"376672cd.39f14e","type":"comment","z":"3369677a.74aeb8","name":"WiPy's","info":"","x":158,"y":194,"wires":[]},{"id":"6959ecf0.0a0614","type":"debug","z":"3369677a.74aeb8","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","x":690,"y":260,"wires":[]},{"id":"838beac4.749028","type":"debug","z":"3369677a.74aeb8","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","x":630,"y":100,"wires":[]},{"id":"9590589.0e58ea8","type":"mqtt in","z":"3369677a.74aeb8","name":"","topic":"home/+/beacon/device/heartbeat","qos":"0","datatype":"auto","broker":"20502e04.4f7d22","x":260,"y":340,"wires":[["6959ecf0.0a0614","fd6e9c8a.f1445"]]},{"id":"29862159.36d95e","type":"influxdb batch","z":"3369677a.74aeb8","influxdb":"140e195f.cd0b67","precision":"","retentionPolicy":"","name":"","x":840,"y":340,"wires":[]},{"id":"20502e04.4f7d22","type":"mqtt-broker","z":"","name":"Pi","broker":"192.168.69.2","port":"1883","clientid":"","usetls":false,"compatmode":true,"keepalive":"60","cleansession":true,"birthTopic":"","birthQos":"0","birthPayload":"","closeTopic":"","closeQos":"0","closePayload":"","willTopic":"","willQos":"0","willPayload":""},{"id":"c598a3ff.40fa6","type":"influxdb","z":"","hostname":"192.168.69.4","port":"8086","protocol":"http","database":"Ruuvi","name":"Ruuvi","usetls":false,"tls":"c01d971f.348e88"},{"id":"52d8d338.02671c","type":"influxdb","z":"","hostname":"192.168.69.4","port":"8086","protocol":"http","database":"TLM","name":"","usetls":false,"tls":"c01d971f.348e88"},{"id":"6e88ee26.41e24","type":"influxdb","z":"","hostname":"192.168.69.4","port":"8086","protocol":"http","database":"unknownBeacons","name":"UnknownBeacons","usetls":false,"tls":"c01d971f.348e88"},{"id":"140e195f.cd0b67","type":"influxdb","z":"","hostname":"192.168.69.4","port":"8086","protocol":"http","database":"Pycom","name":"Pycom","usetls":false,"tls":"c01d971f.348e88"},{"id":"c01d971f.348e88","type":"tls-config","z":"","name":"local-tls","cert":"","key":"","ca":"","certname":"","keyname":"","caname":"","verifyservercert":false}]

```
## Grafana

Before importing the dashboard the databases need to be added as a datasource.
Instruction:
https://grafana.com/docs/features/datasources/influxdb/

## Grafana - Pycom Health

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 3,
  "links": [],
  "panels": [
    {
      "cacheTimeout": null,
      "datasource": "Pycom",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "links": [],
      "options": {
        "displayMode": "basic",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "mappings": [],
            "max": 250000,
            "min": 0,
            "thresholds": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "#EAB839",
                "value": 23000
              },
              {
                "color": "red",
                "value": 25000
              }
            ],
            "unit": "bytes"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "MAC: $tag_edgeMac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "edgeMac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "PycomHealth",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "memFree"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Mem Free",
      "type": "bargauge"
    },
    {
      "cacheTimeout": null,
      "datasource": "Pycom",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 3,
      "links": [],
      "options": {
        "displayMode": "basic",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "mappings": [],
            "max": 2419200,
            "min": 0,
            "thresholds": [
              {
                "color": "dark-orange",
                "value": null
              },
              {
                "color": "light-orange",
                "value": 302400
              },
              {
                "color": "super-light-green",
                "value": 604800
              },
              {
                "color": "light-green",
                "value": 1209600
              },
              {
                "color": "semi-dark-green",
                "value": 1814400
              },
              {
                "color": "dark-green",
                "value": 2419200
              }
            ],
            "unit": "s"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_edgeMac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "edgeMac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "PycomHealth",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "uptime"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Uptime",
      "type": "bargauge"
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Pycom",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 9
      },
      "id": 4,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "MAC: $tag_edgeMac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "edgeMac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "PycomHealth",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "memFree"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Mem Free",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Pycom",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 9
      },
      "id": 5,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "Mac: $tag_edgeMac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "edgeMac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "PycomHealth",
          "orderByTime": "ASC",
          "policy": "default",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "uptime"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Uptime",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 19,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "Pycom Boards",
  "uid": "4IvnakhWk",
  "version": 9
}
```

## Grafana - Ruuvi Tags

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "datasource": "Ruuvi",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "decimals": 2,
            "mappings": [],
            "max": 60,
            "min": 0,
            "thresholds": [
              {
                "color": "blue",
                "value": null
              },
              {
                "color": "green",
                "value": 17.5
              },
              {
                "color": "yellow",
                "value": 35
              },
              {
                "color": "red",
                "value": 45
              }
            ],
            "unit": "celsius"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "temp"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "Mac",
              "operator": "!=",
              "value": "0117C53953DD"
            }
          ]
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Ruuvi Temp",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "datasource": "Ruuvi",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 6,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "decimals": 2,
            "mappings": [],
            "max": 4,
            "min": 0,
            "thresholds": [
              {
                "color": "red",
                "value": null
              },
              {
                "color": "green",
                "value": 1.8
              }
            ],
            "unit": "mvolt"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "battery"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "Mac",
              "operator": "!=",
              "value": "0117C53953DD"
            }
          ]
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Ruuvi Battery",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "datasource": "Ruuvi",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 9
      },
      "id": 3,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "mappings": [],
            "max": 100,
            "min": 0,
            "thresholds": [
              {
                "color": "red",
                "value": null
              },
              {
                "color": "#EF843C",
                "value": 20
              },
              {
                "color": "#EAB839",
                "value": 40
              },
              {
                "color": "light-green",
                "value": 60
              },
              {
                "color": "dark-green",
                "value": 70
              },
              {
                "color": "light-blue",
                "value": 80
              },
              {
                "color": "dark-blue",
                "value": 100
              }
            ],
            "unit": "humidity"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "humidity"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "Mac",
              "operator": "!=",
              "value": "0117C53953DD"
            }
          ]
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Ruuvi Humidity",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "datasource": "Ruuvi",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 9
      },
      "id": 4,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "decimals": 2,
            "mappings": [],
            "max": 1100,
            "min": 800,
            "thresholds": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "#E24D42",
                "value": 275
              },
              {
                "color": "#1F78C1",
                "value": 412.5
              },
              {
                "color": "#EAB839",
                "value": 550
              },
              {
                "color": "#BA43A9",
                "value": 687.5
              },
              {
                "color": "#6ED0E0",
                "value": 825
              },
              {
                "color": "#EF843C",
                "value": 962.5
              },
              {
                "color": "red",
                "value": 1100
              }
            ],
            "unit": "pressurehpa"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "pressure"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": [
            {
              "key": "Mac",
              "operator": "!=",
              "value": "0117C53953DD"
            }
          ]
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Ruuvi Pressure",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Ruuvi",
      "fill": 0,
      "fillGradient": 0,
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 18
      },
      "id": 5,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "tAcc"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Ruuvi Total Acceleration",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "transparent": true,
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Ruuvi",
      "fill": 0,
      "fillGradient": 0,
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 29
      },
      "id": 7,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "rssi"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Ruuvi RSSI",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "transparent": true,
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Ruuvi",
      "fill": 0,
      "fillGradient": 0,
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 40
      },
      "id": 8,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Ruuvi_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "temp"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Ruuvi Temp",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "transparent": true,
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "5s",
  "schemaVersion": 19,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "Ruuvi Tags",
  "uid": "FfAH1zhWz",
  "version": 27
}
```

## Grafana - TLM Tags

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 2,
  "links": [],
  "panels": [
    {
      "datasource": "TLM",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "decimals": 2,
            "mappings": [],
            "max": 60,
            "min": -25,
            "thresholds": [
              {
                "color": "super-light-blue",
                "value": null
              },
              {
                "color": "light-blue",
                "value": 0
              },
              {
                "color": "semi-dark-blue",
                "value": 10
              },
              {
                "color": "dark-green",
                "value": 20
              },
              {
                "color": "light-green",
                "value": 30
              },
              {
                "color": "super-light-red",
                "value": 40
              },
              {
                "color": "dark-red",
                "value": 50
              }
            ],
            "unit": "celsius"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "TLM_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "temp"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "TLM Temp",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "datasource": "TLM",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 4,
      "options": {
        "displayMode": "gradient",
        "fieldOptions": {
          "calcs": [
            "mean"
          ],
          "defaults": {
            "decimals": 2,
            "mappings": [],
            "max": 4,
            "min": 0,
            "thresholds": [
              {
                "color": "red",
                "value": null
              },
              {
                "color": "green",
                "value": 1.8
              }
            ],
            "unit": "mvolt"
          },
          "override": {},
          "values": false
        },
        "orientation": "vertical"
      },
      "pluginVersion": "6.3.6",
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "null"
              ],
              "type": "fill"
            }
          ],
          "measurement": "TLM_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "battery"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "Ruuvi Battery",
      "transparent": true,
      "type": "bargauge"
    },
    {
      "aliasColors": {},
      "bars": false,
      "cacheTimeout": null,
      "dashLength": 10,
      "dashes": false,
      "datasource": "TLM",
      "fill": 0,
      "fillGradient": 0,
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 9
      },
      "id": 6,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "links": [],
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pluginVersion": "6.3.6",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "Mac: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "TLM_Data",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "rssi"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Ruuvi RSSI",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "transparent": true,
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 19,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "TLM",
  "uid": "cxcuxkhZk",
  "version": 5
}
```

## Grafana - Unknown Beacons

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 4,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "unknownBeacons",
      "fill": 0,
      "fillGradient": 0,
      "gridPos": {
        "h": 21,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "alias": "MAC: $tag_Mac",
          "groupBy": [
            {
              "params": [
                "$__interval"
              ],
              "type": "time"
            },
            {
              "params": [
                "Mac"
              ],
              "type": "tag"
            },
            {
              "params": [
                "linear"
              ],
              "type": "fill"
            }
          ],
          "measurement": "Unknown_Beacon",
          "orderByTime": "ASC",
          "policy": "autogen",
          "refId": "A",
          "resultFormat": "time_series",
          "select": [
            [
              {
                "params": [
                  "rssi"
                ],
                "type": "field"
              },
              {
                "params": [],
                "type": "mean"
              }
            ]
          ],
          "tags": []
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "RSSI",
      "tooltip": {
        "shared": false,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 19,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "Unknown Tags",
  "uid": "_7o1TmhWk",
  "version": 3
}
```
