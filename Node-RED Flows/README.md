## Node-RED Flows

The example is provided to provide easy parsing of the mqtt messages into Influx DB.

It is assumed that the following datbases have been created:
* unknownBeacons
* TLM
* Ruuvi

If influx has bee installed the following can be run to create the databases:

```bash
#Enter influx console
influx
#create each database
CREATE DATABASE unknownBeacons
CREATE DATABASE TLM
CREATE DATABASE Ruuvi
```

