
#
# File: load_files.py
# load sys files and application files
# The data is stored in the following
#    System Files are stored in the following in json format
#    	As a dictionary with the key of FILES:SYS
#    	The key of the dictionary are the file names
#    APP Files are stored in the following in json format
#    	As a dictionary with the key of
#    	The key of the dictionary are the file names

#  import redis
#  make redis dictionary "SYS:FILES"
# store json_object to redis data "global_sensors"
import os
from os import listdir
from os.path import isfile, join
import redis
import json
import msgpack
from  .cloud_handlers_py3 import Cloud_TX_Handler
from  .construct_data_handlers_py3 import Redis_Hash_Dictionary
sys_files = "system_data_files/"

import base64


   
class BASIC_FILES( object ):
    def __init__(self, redis_handle,path, redis_site,label):
        self.path = path
        self.redis_site = redis_site
        self.cloud_handler = Cloud_TX_Handler(redis_handle)

        self.redis_handle = redis_handle
        self.key = "[SITE:"+redis_site["site"]+"][FILE:"+label+ "]"
        self.hash_driver = Redis_Hash_Dictionary(self.redis_handle,self.key,None,self.cloud_handler)

    def file_directory(self):
        return self.hash_driver.hkeys()

    def delete_file(self, name):
        self.hash_driver.hdelete(name)

        
    def save_file(self, name, data):
        f = open(self.path + name, 'w')
        json_data = json.dumps(data)
        f.write(json_data)
        self.hash_driver.hset( name,data)

    def load_file(self, name):
        return self.hash_driver.hget(name)
 

       

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,sys_files,redis_site,"SYS" )
    
 

if __name__ == "__main__":


   def load_file( file_list,path, redis_key):
       for i in files:
           fileName, fileExtension = os.path.splitext(i)
           if fileExtension == ".json":
               f = open(path+i, 'r')
               data = f.read()
               temp = json.loads(data) # test to ensure data has json format
               pack_data = msgpack.packb(temp)
               pack_data = base64.b64encode(pack_data)
               redis_handle.hset( redis_key, i , pack_data)


 

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()

   redis_site = json.loads(data)

   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_file_db"], decode_responses=True)




   key = "[SYSTEM:"+redis_site["site"]+"][FILE:"
   redis_handle.delete(key+"APP]")
   redis_handle.delete(key+"SYS]")
   redis_handle.delete(key+"LIMITS]")


   # load sys files

   files = [ f for f in listdir(sys_files)  ]
   load_file( files,sys_files, key+"SYS]" )

  

else:
   pass


__TEST__= False   
if __TEST__ == True:
   app_file_handler = APP_FILES( redis_handle,redis_site )
   sys_file_handler = SYS_FILES( redis_handle,redis_site)
   print(app_file_handler.file_directory())
   directory_list = app_file_handler.file_directory()
   print(app_file_handler.load_file(directory_list[0]))
   
