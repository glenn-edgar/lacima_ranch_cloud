import redis
import json


class Construct_Applications(object):

   def __init__(self,bc,cd):  # bc is build configuration class cd is construct data structures
       bc.add_header_node("APPLICATION_SUPPORT")
       bc.end_header_node("APPLICATION_SUPPORT")
       
       

