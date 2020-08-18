from influxdb import InfluxDBClient
import json
import config
import ble2


def INFLUX():
    global client
    client = InfluxDBClient()