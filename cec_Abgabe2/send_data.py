#!/usr/bin/env python3

import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from azure.iot.device import IoTHubDeviceClient
from datetime import datetime
import json

connection_string = "HostName=ampaduHub.azure-devices.net;DeviceId=humditySensor;SharedAccessKey=+d4ir+BJj/+jVfyRb4nikJqqARASa98pAsfzCKU7ZZI="
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)

def send_message(message):
    print("Sending message:", message)
    device_client.send_message(message)

if __name__ == "__main__":
   try:
      device_client.connect()
      i2c = busio.I2C(board.SCL, board.SDA)
      ads = ADS.ADS1015(i2c)
      chan = AnalogIn(ads, ADS.P0)

      while True:
         message = {"deviceId":"sensor", "humidity":chan.value, "voltage":chan.voltage, "ts":str(datetime.now())}
         send_message(json.dumps(message))
         time.sleep(2)
    
   except KeyboardInterrupt:
      print("Stopped by user")
   finally:
      device_client.disconnect()
