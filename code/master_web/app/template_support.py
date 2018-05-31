#
#
# This is Support for Drawing Bullet Charts
#
#
#
#
#
#
#

''' 
This is the return json value to the javascript front end  
{ "canvasName":"canvas1","featuredColor":"Green", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 1" },
                                             { "canvasName":"canvas2","featuredColor":"Blue", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 2" },
                                             { "canvasName":"canvas3","featuredColor":"Red", "featuredMeasure":14.5,
                                                "qualScale1":14.5, "qualScale1Color":"Black","titleText":"Step 3" },
'''

class template_support():

   def __init__(self , redis_handle, statistics_module):
       self.redis_handle       = redis_handle
       self.statistics_module  = statistics_module


   def  generate_current_canvas_list( self, schedule_name, *args, **kwargs ):
       return_value = []
       
       self.schedule_name = schedule_name
       data = self.statistics_module.schedule_data[ schedule_name ]

       current_data      = self.statistics_module.get_current_data( data["step_number"],schedule_name )
       limit_values      = self.statistics_module.get_current_limit_values( data["step_number"],schedule_name )
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           temp["qualScale1"]                  = limit_values[i]['limit_avg']
           temp["featuredMeasure"]             = current_data[i] 
           temp["limit"]                       = limit_values[i]['limit_std']
           temp["step"]                        = i
           return_value.append(temp)
           
       return return_value
          



        
   def generate_canvas_list(self, schedule_name, flow_id ,  *args,**kwargs):
       return_value = []
       
       self.schedule_name = schedule_name
       data = self.statistics_module.schedule_data[ schedule_name ]
       flow_sensors = self.statistics_module.sensor_names 
       flow_sensor_name = flow_sensors[flow_id]

       conversion_rate   = self.statistics_module.conversion_rate[flow_id]

       flow_data      = self.statistics_module.get_average_flow_data( data["step_number"], flow_sensor_name, schedule_name )
       limit_values = self.statistics_module.get_flow_limit_values( data["step_number"], flow_sensor_name, schedule_name )
       
       for i in limit_values:
           try:
               i['limit_avg'] = float(i['limit_avg'])*conversion_rate
               i['limit_std'] = float(i['limit_std'])*conversion_rate
           except:
               pass
          
       corrected_flow = []
       for i in flow_data:
           temp1 = []
           
           for j in i:
               temp1.append( j *conversion_rate)
           corrected_flow.append(temp1)
       
       
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           try:
                temp["qualScale1"]             = limit_values[i]['limit_avg']
           except:
                temp["qualScale1"]             = 0

           try:
               temp["featuredMeasure"]         = corrected_flow[i]
           except:
               temp["featuredMeasure"]         = 0
           try:
               temp["limit"]                       = limit_values[i]['limit_std']
           except:
               temp["limit"]                   = 0
           return_value.append(temp)
           
       return return_value



