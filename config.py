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