# GridPot code
# switch object class for integrating with a GridLAB-D simulation instance
# Author: sk4ld

import logging
import urllib2
logger = logging.getLogger(__name__)

from GL_obj import GL_obj


# base object class for integrating with a GridLAB-D simulation instance
class GL_TRANSFORMER(GL_obj):
    def init_params(self):
        # Here we define what we want to poll for this object. 
        # We dont necessarily want to have a setter for each one of these
        # Nor do we necessarily have to display each of these to the HMI
        self.params["status"] = ""
        self.params["phases"] = ""
        self.params["from"] = ""
        self.params["to"] = ""
        self.params["ambient_temperature"] = ""
        self.params["winding_hot_spot_temperature"] = "" # Not sure exactly what this is
        self.params["configuration "] = ""  # This one is a config file, is complicated to update/set


    # OVERLOADED http display for the conpot built in http hmi
    def http_display(self):
        ht_format = "<table border=0>\n"
        ht_format += "<tr>\n"
        ht_format += "  <td>"+ self.obj_name +"</td>\n"
        ht_format += "  <td></td>\n"
        ht_format += "</tr>\n"
        for x in ('status', 'phases', 'from', 'to', 'ambient_temperature'):            
            ht_format += "<tr>\n"        
            ht_format += "  <td>" + x + "</td>\n"
            ht_format += "  <td>" + self.params[x] + "</td>\n"
            ht_format += "<tr>\n"        
        return ht_format
