
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

import os
from os import listdir
from os.path import isfile, join
import redis
import json
import msgpack

from  .construct_data_handlers_py3 import Redis_Hash_Dictionary
from  .cloud_handlers_py3 import Cloud_TX_Handler
from .graph_query_support_py3 import Query_Support
from .find_sites_py3 import Find_Redis_Site_Data
from .find_sites_py3 import Find_Sites
   
class BASIC_FILES( object ):
    def __init__(self, redis_handle,path, site,label):
        
        self.path = path
        self.site = site
        
        data = {}
        data["forward"] = True
        self.cloud_handler = Cloud_TX_Handler(redis_handle)
        self.redis_handle = redis_handle
        self.key = "[SITE:"+site+"][FILE:"+label+ "]"
        
        self.hash_driver = Redis_Hash_Dictionary(self.redis_handle,data,self.key,self.cloud_handler)

    def file_exists(self,name):
        print("self.path",self.path+self.site+"/",name,isfile(self.path+name))
        return isfile(self.path+self.site+"/"+name)


    def file_directory(self):
        return self.hash_driver.hkeys()

    def delete_file(self, name):
        self.hash_driver.hdelete(name)

    
        
    def save_file(self, name, data):
        print("saving file")
        f = open(self.path+self.site+"/" + name, 'w')
        json_data = json.dumps(data)
        f.write(json_data)
        self.hash_driver.hset( name,json_data)

    def load_file(self, name):
        
        print("******************name",name,self.key)
        return json.loads(self.hash_driver.hget(name))
 

class APP_FILES( BASIC_FILES ):
   def __init__( self, redis_handle,site ):
       BASIC_FILES.__init__(self,redis_handle,"app_data_files/", site,"APP" )
       

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle,site ):
        BASIC_FILES.__init__(self,redis_handle,"system_data_files/",site,"SYS" )
    
        
class LIMIT(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,"limit_data_files/",site,"LIMITS" )


if __name__ == "__main__":

   file_directories = [ ["system_data_files/","SYS"], 
                          ["app_data_files/","APP"], ["limit_data_files/","LIMIT"] ]


   
   find_site_data = Find_Redis_Site_Data()
   redis_site_data = find_site_data.find_site_data("system_data_files")
   redis_handle = redis.Redis(redis_site_data["host"], 
                                    redis_site_data["port"], 
                                    db=redis_site_data["redis_file_db"])
                                    
   find_sites = Find_Sites(redis_site_data)
   
   sites = find_sites.determine_sites()
   
   cloud_handler_tx = Cloud_TX_Handler(redis_handle)
   forward = {"forward":True}  
   
   #  construct sub directories for sites in each of the catagory directories
   for i in file_directories:
       for j in sites:
         
          try:
            
             os.mkdir(os.path.join(i[0],j))
          except :
             pass

   # no lets load the files in
   
   for i in file_directories:
       
       for j in sites:
           
           path = os.path.join(i[0],j)
           
           raw_files = listdir(path)
           
           files = []
           for k in raw_files:
               
               if k.split(".")[-1] == "json":
                  files.append(k) 
           
           if len(files) == 0:
              continue
           
           # now load files into redis
           key = "[SITE:"+j+"][FILE:"+i[1]+"]"
           old_fields = redis_handle.hkeys(key) 
           
           for field_name in files:
               try:
                  
                   extension = field_name.split(".")[1]
                   if extension != "json":
                       continue
               
                   file_name = os.path.join(path,field_name)
                   file_handle = open(file_name,'r')
                   data = file_handle.read()
                   file_handle.close()
                    
                   pack_data = msgpack.packb(data, use_bin_type = True )
                   
                   redis_pack_data = redis_handle.hget(key,field_name)
                   if redis_pack_data != None:
                        redis_file_data = msgpack.unpackb(redis_pack_data,encoding='utf-8')
                   else:
                        redis_file_data = None
                   
                   if redis_file_data != data:
                       redis_handle.hset(key,field_name,pack_data)
                       cloud_handler_tx.hset(forward,key,field_name,pack_data)
                   else:
                       pass #print("file match",field_name)
               except:
                  raise
               
           new_fields = set(redis_handle.hkeys(key))
           # remove old keys
           fields_to_delete = set(old_fields)-set(new_fields)
          
           for m in list(fields_to_delete):
               
               redis_handle.hdel(key,m)
               cloud_handler_tx.hdel(forward,key,m)
           

else:
   pass


__TEST__= False
if __TEST__ == True:
   print("made it to test")
   app_file_handler = APP_FILES( redis_handle,"LaCima" )
   sys_file_handler = SYS_FILES( redis_handle,"LaCima")
   print(app_file_handler.file_directory())
   directory_list = app_file_handler.file_directory()
   for i in directory_list:
       app_file_handler.load_file(i)

   print(sys_file_handler.file_directory())
   directory_list =sys_file_handler.file_directory()
   for i in directory_list:
       sys_file_handler.load_file(i)
  
else:
   pass
   

