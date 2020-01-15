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
#optional database for hearbeat
CREATE DATABASE linux
```

If you are missing any nodes a warning will pop up to display they are missing and the node will be blanked out. Go to Manage pallete to add these Nodes.

Once the flow has been imported and all Nodes have been installed the databases will need configured for each 'influx batch node'.
