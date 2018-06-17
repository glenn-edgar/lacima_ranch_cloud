
import redis
import msgpack
import json
import zlib
from .redis_stream_utilities_py3 import Redis_Stream

class Send_Object(object):
   def __init__(self, redis_handle, transport_queue, queue_depth ):
       self.redis_handle = redis_handle
       self.transport_queue = transport_queue
       self.queue_depth = queue_depth
       
       


   def send(self,action,**kwargs):
       kwargs["ACTION"] = action      
       kwargs_pack = msgpack.packb(kwargs, use_bin_type = True)
       

       self.redis_handle.lpush(self.transport_queue,kwargs_pack )
       self.redis_handle.ltrim(self.transport_queue, 0,self.queue_depth)
       
       

   def length(self):
       return self.redis_handle.llen(self.transport_queue)
   
   def determine_site(self,key):
       temp = key.split("[SITE:",maxsplit=1)[1]
       temp = temp.split("]",maxsplit=1)[0]
       return temp

       
   def extract(self):
 
       
       length = self.redis_handle.llen(self.transport_queue)
       if length == 0:
          return []
       
       packed_data = self.redis_handle.rpop(self.transport_queue)
       unpacked_data = msgpack.unpackb(packed_data,encoding='utf-8' )
       
       
       site = self.determine_site(unpacked_data['key'])
       
       return [site,packed_data]

 
         
       
       

class Cloud_TX_Handler(Send_Object):

   def __init__(self, redis_handle, transport_queue = "_TRANSPORT_QUEUE_" , transport_depth = 128 ):
       Send_Object.__init__(self,redis_handle,transport_queue,transport_depth)
       self.redis_handle = redis_handle

   def check_forwarding(self, data):  # do not forward data structures unless specified in the "forward" field
       if  "forward" in data:
           if data["forward"] == True:
              return True
       return False

   def delete(self,forward_data,key):
       if self.check_forwarding(forward_data):
           self.send("DEL",key=key)
 

 
   def hset(self,forward_data,key,field,data):
       if self.check_forwarding(forward_data):
           self.send("HSET",key=key,field=field,data = data )
       
   def hdel(self,forward_data,key,field):
       if self.check_forwarding(forward_data):
           self.send("HDEL",key=key,field=field)
       
   def lpush(self,forward_data,depth, key, data):
       if self.check_forwarding(forward_data):
           self.send("LPUSH",key=key,depth=depth,data = data)
       
   def list_delete(self, forward_dat,key,index):
       if self.check_forwarding(forward_dat):
           self.send("LIST_DELETE",key=key,index = index)
       
   def rpop(self,forward_dat,key):
       if self.check_forwarding(forward_dat):
           self.send("RPOP",key=key)
       
   def stream_write(self,forward_dat,depth, id, key,  store_dictionary_pack ):
       if self.check_forwarding(forward_dat):
           self.send("STREAM_WRITE",id=id,key=key,depth=depth , store_dictionary = store_dictionay_pack )
       
   def stream_list_write(self, forward_dat,depth, key,data ):
       if self.check_forwarding(forward_dat):
           self.send("STREAM_LIST_WRITE", key=key,depth =depth,data = data)
       
       
class Cloud_RX_Handler(object):

   def __init__(self,redis_handle,redis_site_data,site_list,*args):    
      self.redis_handle = redis_handle
      self.redis_site_data = redis_site_data
      self.site_list = site_list
      self.data_handlers = {}
      self.data_handlers["DEL"] = self.delete
    
      self.data_handlers["HSET"] = self.hset
      self.data_handlers["HDEL"] = self.hdel
      self.data_handlers["LPUSH"] = self.lpush
      self.data_handlers["LIST_DELETE"] = self.list_delete
      self.data_handlers["RPOP"] = self.rpop
      self.data_handlers["STREAM_WRITE"] = self.stream_write
      self.data_handlers["STREAM_LIST_WRITE"] = self.stream_list_write
      self.redis_stream =  Redis_Stream(redis_handle, exact_flag = False)
      self.file_path = {}
      self.file_path["APP"] =  "app_data_files/"
      self.file_path["SYS"] =  "system_data_files/"
      self.file_path["LIMIT"]  = "limit_data_files/"
      self.site_list = site_list
      
   def unpack_remote_data( self,topic, list_data):
      #
      # Find Site
      #  
      #
      topic_list = topic.split("/")
      site = topic_list[-1]
      print(site in self.site_list)
      if site not in self.site_list:
           return # unrecognized site 
      
      for i_pack in list_data:
          
          i = msgpack.unpackb(i_pack, encoding='utf-8')
          i["SITE"] = site
          action = i["ACTION"]
          print("download",i)
          if action in self.data_handlers:
              self.data_handlers[action](i)
          else:
              raise ValueError("Bad Action ID")

 
   def check_for_file(self,key):
       
       self.file_type = None
       fields = key.split("[FILE:")
       if len(fields) > 1:
          self.file_type = fields[1].split("]")[0]
          return_value = True
       else:
          return_value = False
       
       print(return_value,self.file_type)
       return return_value

   def delete(self,key):
       self.redis_handle.delete(key)
 

   def save_raw_file(self,path,name,data): 
       f = open(path + name, 'w')
       f.write(data)
       f.close()
 
 
              
   def hset(self,data):
       self.redis_handle.hset(data["key"],data["field"],data["data"])
       if self.check_for_file(data["key"]) == True:
          
          print(self.file_type,self.file_path, self.file_type in self.file_path)
          if self.file_type in self.file_path:
               
               path = self.file_path[self.file_type]+data["SITE"]+"/"
               file = data["field"]
               temp_data = msgpack.unpackb(data["data"], encoding='utf-8')
               
               self.save_raw_file(path,file,temp_data)
       
   def hdel(self,data):
      self.redis_handle.hdel(data["key"],data["field"] )
       
   def lpush(self, data):
       self.redis_handle.lpush(data["key"],data["data"])
       self.redis_handle.ltrim(data["key"],0, data["depth"])

       
   def list_delete(self,data):
       if self.redis_handle.exists(data["key"]) == True:
           self.redis_handle.lset(data["key"], data["index"],"__#####__")
           self.redis_handle.lrem(data["key"], 1,"__#####__") 

       
   def rpop(self,data):
       self.redis_handle.rpop(data["key"])
       
   def stream_write(self,data ):
       print("stream write data",data)
       self.redis_stream.xadd(key = data["key"], max_len= data["depth"],id=data["id"],data_dict=data["store_dictionary"] )
   
   
   def stream_list_write(self, data ):
       self.redis_handle.lpush(data["key"],data["data"])
       self.redis_handle.ltrim(data["key"],0,data["depth"]-1)
    

if __name__ == "__main__":
  pass