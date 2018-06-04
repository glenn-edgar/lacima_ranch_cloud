# file build system
#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
from  build_configuration_py3 import Build_Configuration
from  construct_data_structures_py3 import Construct_Data_Structures
from  graph_modules_py3.build_cloud_py3 import Build_Cloud
from  graph_modules_py3.build_lacima_py3 import Site_Template_LaCima


if __name__ == "__main__" :

   file_handle = open("../code/system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data) 
   bc = Build_Configuration(redis_site)
   cd = Construct_Data_Structures(redis_site["site"],bc)
   
   #
   #
   # Construct Systems
   #
   #
   bc.add_header_node( "SYSTEM","main_operations" )
                                                  

   Build_Cloud(bc,cd,"Cloud")
   Site_Template_LaCima(bc,cd,"LaCima")

 
   bc.end_header_node("SYSTEM")
   bc.check_namespace()
   bc.store_keys()
   bc.extract_db()
   bc.save_extraction("../code/system_data_files/extraction_file.pickle")
   bc.delete_all()
   #bc.restore_extraction("extraction_file.pickle")
   #bc.delete_all()


 