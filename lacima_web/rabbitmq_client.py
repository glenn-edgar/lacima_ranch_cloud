#!/usr/bin/env python
import pika
import uuid
import json
import os
import time
import redis
import rabbitmq_client
import zlib

import msgpack




class RabbitMq_Client(object):
    def __init__(self,server,port,username,password,vhost,queue):
         self.queue     = queue
         self.queue = "_web_rpc_queue"
         print("vhost",self.queue,vhost)


         credentials = pika.PlainCredentials( username, password )
         parameters = pika.ConnectionParameters( server,
                                                 port,  #ssl port
                                                 vhost,
                                                 credentials,
                                                 ssl = True )
         parameters.heartbeat = 20
         self.connection = pika.BlockingConnection(parameters)        
         self.channel = self.connection.channel()
         result = self.channel.queue_declare(exclusive=True)
         self.callback_queue = result.method.queue
         
         self.channel.basic_consume(self.on_response, no_ack=False,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        
        print("madie it here body")
        try:
           body = msgpack.unpackb(body)
        except Exception as e: 
           print(str(e))      
        print(type(body),len(body))
        print(body.keys())
        if self.corr_id == props.correlation_id:
            temp_1 = body["results"]
         
 
            print("made it here 1")
            
            body["results"] = msgpack.unpackb(zlib.decompress(temp_1))
            print("made it here 3")
            self.response = body
            print("self.respno",self.response)
            
     

    def call(self, data, time_out ):
      try:
        
        time_out = time_out 
        input_data = msgpack.packb(json.dumps(data))
        

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key= self.queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body= input_data)
        print("time_out",time_out,self.response)
        while self.response is None:
                 print("time_out",time_out,self.response)

                 self.connection.process_data_events()
              
                 time_out = time_out -1
                 if time_out == 0:
                
                     data = {}
                     data["reply"] = "No Connections"
                     data["results"] = None
                     return data
                 else:
                    time.sleep(.2)
        self.close()
       
        return self.response
      except:
                     data = {}
                     data["reply"] = "No Connections"
                     data["results"] = None
                     self.close()
                     return data

    def close( self ):
        self.channel.close()


if __name__ == "__main__":
   
   vhost = "LaCima"
   redis_startup    = redis.StrictRedis( host = "localhost", port=6379, db = 2 )   
   username              = redis_startup.hget(vhost,"rabbit_username" )
   password              = redis_startup.hget(vhost,"rabbit_password" )
   server                = redis_startup.hget(vhost,"rabbit_server"   )
   port                  = int(redis_startup.hget(vhost,"rabbit_port"     ) )
   queue                 = redis_startup.hget(vhost,"rabbit_queue" )
   # vhost is not defined --- possible error for test condition
   remote_interface = RabbitMq_Client(server,port,username,password,"LaCima",queue)
   print "rabbitmq queue constructed"
   remote_interface.close()
   print "rabbitmq queue closed"
