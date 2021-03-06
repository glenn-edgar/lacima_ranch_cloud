
#
#
import json
import msgpack

import redis
import time
import copy
import zlib




import paho.mqtt.client as mqtt
import ssl

from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.mqtt_client_py3 import MQTT_CLIENT

from redis_support_py3.load_files_py3 import APP_FILES 
from redis_support_py3.load_files_py3 import SYS_FILES 


class Redis_Cloud_Upload(object):

   def __init__(self,redis_site_data,redis_handle):
 
       self.redis_handle = redis_handle                                     
       
       self.mqtt_client = MQTT_CLIENT(redis_site_data,
                                      redis_site_data["mqtt_cloud_server"],
                                      redis_site_data["mqtt_cloud_port"],
                                      "cloud",
                                      "mosquitto_local",
                                      certfile= "../mosquitto/certs/server.crt", 
                                      keyfile= "../mosquitto/certs/server.key", 
                                      cert_reqs=ssl.CERT_NONE )
     
       self.redis_site_data = redis_site_data
                                           
       self.tx_handler = Cloud_TX_Handler(self.redis_handle)
  
       
       self.state = "CONNECT"
       
       self.packet_data = None
       self.topic = redis_site_data["mqtt_upload_topic_base"]
       #print("topic",self.topic)
       self.temp_queue = "__CLOUD_UPLOAD_TEMP_QUEUE__"
       self.do_start()
       
   def do_connect(self):
      #print("***************************connect state******************************************************")
      status = self.mqtt_client.connect()
      if status == True:
         self.state = "MONITOR"
      else:
         self.state == "CONNECT"
      
   def do_monitor(self):
       while True:
           #print("*****************monitor state*************",time.time())
           if self.packet_data == None:
              length = self.tx_handler.length()
              #print("length",length)
              if length == 0:
                  return

              self.packet_data = self.tx_handler.extract()
              #print(type(self.packet_data),self.packet_data)
              site = self.packet_data[0]
              self.packet_data[1] = zlib.compress(self.packet_data[1])
      
           payload = copy.deepcopy(self.packet_data)
           #print("topic",self.topic+payload[0])
           return_value = self.mqtt_client.publish(self.topic+payload[0],payload=payload[1],qos=2)
           
           if return_value[0] == True:
                self.packet_data = None
           
           else:
              #print("*********************************** bad publish **************")
              self.mqtt_client.disconnect()
              time.sleep(5)
              self.mqtt_client = MQTT_CLIENT(self.redis_site_data,redis_site_data["mqtt_cloud_server"],redis_site_data["mqtt_cloud_port"],"remote","mosquitto_cloud")
              self.state = "CONNECT"  

              return # error lets try to reconnect         
       
      
   def do_start(self):
      while True:
        if self.state == "CONNECT":
           self.do_connect()
        else:
           self.do_monitor()
           #print("end monitor")
        time.sleep(.1)
        
if __name__ == "__main__":
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
      
   redis_site_data = json.loads(data)
   redis_handle = redis.Redis(redis_site_data["host"], 
                                    redis_site_data["port"], 
                                    db=redis_site_data["redis_file_db"])

   Redis_Cloud_Upload(redis_site_data,redis_handle)
        
