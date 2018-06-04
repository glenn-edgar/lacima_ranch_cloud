import json
import redis
import os
import os.path
from .graph_query_support_py3 import Query_Support



class Find_Redis_Site_Data(object):
   def __init__(self):
       pass


   def find_site_data(self,base_path ):
       file_name = os.path.join(base_path,"redis_server.json")
       file_handle = open(file_name,'r')
       data = file_handle.read()
       file_handle.close()
       redis_site_data = json.loads(data)
       return redis_site_data



class Find_Sites(object):
   def __init__(self,redis_site_data):
       self.redis_handle = redis.StrictRedis( host = redis_site_data["host"] , 
                                         port=redis_site_data["port"], 
                                         db=redis_site_data["graph_db"] , 
                                         decode_responses=True)
       self.query_support = Query_Support(redis_site_data["host"],
                                          redis_site_data["port"],
                                          redis_site_data["graph_db"] )

   def determine_sites(self):
       query_list = []
       self.query_support.add_match_terminal(  query_list, "SITE" )
       site_nodes,site_nodes_data = self.query_support.match_list(query_list)
       directory_list = []
       for i in site_nodes_data:
           directory_list.append(i["name"])
       return directory_list
 
