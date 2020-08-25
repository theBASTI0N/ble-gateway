import json

try:
  # Allows for test config file to be used during development
  config = json.load(open('config/testblegateway.json',))
except:
  config = json.load(open('config/blegateway.json',))

def get_config(section):
  if section == 'bleDevice' or section == 'filters' or \
    section == 'identifiers' or section == 'endpoints' or \
      section == 'names':
      return config[section]
  elif section == 'mqtt' or section == 'http' or \
    section == 'influx':
    if section in config:
      return config[section]
  else:
    print('Invalid Section given')
    return None