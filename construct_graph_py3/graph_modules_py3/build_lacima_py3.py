#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import redis


from  .construct_LaCima.construct_applications_py3 import Construct_Applications
from  .construct_LaCima.construct_controller_py3 import Construct_Controllers
from  .construct_LaCima.construct_redis_monitor_py3 import Construct_Redis_Monitoring

class Site_Template_LaCima(object ):

   def __init__(self, bc,cd,site_data):
       bc.add_header_node( "SITE",site_data,  
                            properties = {"url":"https://lacimaRanch.cloudapp.net" } )
       Construct_Applications(bc,cd)
       Construct_Controllers(bc,cd)
       Construct_Redis_Monitoring(bc,cd)
       bc.end_header_node("SITE")
