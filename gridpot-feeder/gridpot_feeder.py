#!/usr/bin/env python
# GridPot Feeder code
# Author: sk4ld
# This feeds data from GridLAB-D into Skyline for anomaly detection. 
# It reads feeder_config.txt for networking and model info.
# feeder_config.txt should be in this same directory. 
# Sample feeder_config.txt file contents:
#[gridlabd]
#logpath=/var/log/skyline/
#gridpotmodel_file = "model.gpm"
#gridlabd_ip = "192.168.1.10"
#gridlabd_port = 6267
#skyline_ip = "localhost"
#skyline_port = 2025
#graphite_ip = 192.168.1.100
#graphite_port = 80
#-----------------------------------------------------------------#

import re
import logging
import urllib2
from urllib import urlencode
import pycurl
import msgpack
import socket
import xml.etree.ElementTree as ET
import io
from time import sleep, time
import ConfigParser, os
from GL_obj import GL_obj
from GL_SWITCH import GL_SWITCH
from GL_TRANSFORMER import GL_TRANSFORMER
from GL_REGULATOR import GL_REGULATOR

#float_complex_pattern = '^([-+]?(\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?[r]?|[-+]?((\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?)?[i]|[-+]?(\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?[r]?[-+]((\d+\.?\d*|\d*\.?\d+)([Ee][-+]?[0-2]?\d{1,2})?)?[i])$' # for values like "+1.02693e+06-0.389154i"
complex_pattern = r'.\d+.\d+\w.'
scientific_pattern = '\s-?[1-9]+[0-9]*.?[0-9]*e-?\+?[0-9]+\s?'
#re.findall('\d+', s)
logger = logging.getLogger(__name__)


# TODO:
# consider https://pypi.python.org/pypi/fastnumbers for faster parsing
def is_complex(s):
    #print "[*] testing: <"+s[:-1]+'j>'
    #if s.count("+") + s.count("-") < 3:
    #    return False
    try:
        complex(s[:-1]+'j') # replace trailing d or i with 'j' for complex
    except ValueError:
        return False
    return True
    
# TODO:
# consider https://pypi.python.org/pypi/fastnumbers for faster parsing
def is_number(s):
    try:
        n=str(float(s))
        if n == "nan" or n=="inf" or n=="-inf" : return False
    except ValueError:
        return is_complex(s)
    return True

# integrates with a GridLAB-D simulation instance and feeds data into Skyline 
# anomaly detection engine
class GridPotFeeder(object):
    def __init__(self, *args):
        self.logger = logging.getLogger('gridpot-feeder')
        self.logger.setLevel(logging.DEBUG)
        
        config = ConfigParser.ConfigParser()
        config.readfp(open('feeder_config.txt'))
        
        self.LOG_PATH = config.get("gridlabd", "logpath")
        self.stdin_path = '/dev/null'
        self.stdout_path = self.LOG_PATH + '/gridpot-feeder.log'
        self.stderr_path = self.LOG_PATH + '/gridpot-feeder.log'
        
        fh = logging.FileHandler(self.stdout_path)
        #fh2 = logging.FileHandler(self.stderr_path)
        fh.setLevel(logging.DEBUG)
        #fh2.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        #self.logger.addHandler(fh2)
        
        self.logger.info("Initializing gridpot-feeder")
        try:
            self.gridpotmodel_file = config.get("gridlabd", "gridpotmodel_file")
            self.gridlabd_ip = config.get("gridlabd",   "gridlabd_ip")
            self.gridlabd_port = config.get("gridlabd", "gridlabd_port") 
            self.skyline_ip = config.get("gridlabd",   "skyline_ip")
            self.skyline_port = config.get("gridlabd", "skyline_port") 
            self.graphite_ip = config.get("gridlabd",   "graphite_ip")
            self.graphite_port = config.get("gridlabd", "graphite_port") 
            self.gridpotmodel = ""
            self.conpot_name = "" #(This is just a placeholder variable)
            self.SCADA_objects = []
        except e:
            self.logger.info("[!] Failed to initialize gridpot-feeder.  Check your feeder_config.txt")
        self.logger.info("Initialized gridpot-feeder")
        #self.initialize()
    
    

        
        
    def get_http(self, key):
        self.logger.info( "[*] get_http("+str(key)+")\n\n")
        #print "[*] self.SCADA_objects="+str(self.SCADA_objects)
        for x in self.SCADA_objects:
            if key == x.obj_name:
                return x.http_display()

    def parse_xml_for_value(self,response):
        # get the value field
        #print 'RESPONSE:'+response
        tree = ET.fromstring(response)
        for child in tree:
            #print "parsing: "+str(child.tag) + ":" + str(child.text)
            if child.tag == 'value':
                return str(child.text)
            
    def poll_gridlabd(self):
        while True:
            sleep(0.02)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for x in self.SCADA_objects:
                self.logger.info("[*]=========================================")
                self.logger.info("[*] " + x.obj_name + " properties:")
                self.logger.info(x.params)
                t = time()
                for prop in x.params:
                    #print "[*] DEBUG: " + str(prop)
                    response = x.poll_gl_object(prop)
                    result = self.parse_xml_for_value(response)
                    
                    if (x.params[prop]!= "" and result != x.params[prop] and x.is_event_parameter(prop)):
                        # send event to graphite!
                        graphite_url = "http://"+str(self.graphite_ip) + ":"+str(self.graphite_port)+"/events/"
                        
                        post_data = '{\"what\": \"Switch '+x.obj_name+' changed status to '+result+'", \"tags\" : \"switch_'+str(result)+'\"}'
                        #postfield = urlencode(post_data)
                        postfield = post_data
                        c = pycurl.Curl()
                        c.setopt(c.URL, graphite_url)
                        c.setopt(c.POSTFIELDS,postfield)
                        
                        self.logger.info("[*] Event update to graphite about: "+str(x.obj_name))
                        self.logger.info("[*] " + str(post_data))
                        x.params[prop] = result
                        c.perform()#may break
                        c.close()
                        
                    else:
                        # Need to numerical-ize the data :)
                        x.params[prop] = result
                        
                        tokens = result.split(" ")
                        for val in tokens:
                            
                            if is_number(val):
                                try:
                                    # send numerical component
                                    fval = float(val)
                                    packet = msgpack.packb((x.station_name+"."+x.obj_name+"."+str(prop), [t, fval ] ))
                                    
                                    sock.sendto(packet, (self.skyline_ip, int(self.skyline_port)))
                                    
                                    self.logger.info( "[*] Sending to " + str(self.skyline_ip) + ":" + str(self.skyline_port)+" : [" + (x.station_name+"."+x.obj_name+"."+str(prop)) +", "+str(fval) + ", " + str(t) +"]"  )
                                except ValueError:
                                    if is_complex(val):
                                        cval = complex(val[:-1]+'j')
                                        
                                        # send real component
                                        packet = msgpack.packb((x.station_name+"."+x.obj_name+"."+str(prop)+"_r", [t, cval.real ] ))
                                        
                                        sock.sendto(packet, (self.skyline_ip, int(self.skyline_port)))
                                        
                                        self.logger.info( "[*] Sending to " + str(self.skyline_ip) + ":" + str(self.skyline_port)+" : [" + (x.station_name+"."+x.obj_name+"."+str(prop))+"_r" +", "+str(cval.real) + ", " + str(t) +"]"  )
                                        # send imaginary component
                                        packet = msgpack.packb((x.station_name+"."+x.obj_name+"."+str(prop)+"_i", [t, cval.imag ] ))
                                        
                                        sock.sendto(packet, (self.skyline_ip, int(self.skyline_port)))
                                        
                                        self.logger.info( "[*] Sending to " + str(self.skyline_ip) + ":" + str(self.skyline_port)+" : [" + (x.station_name+"."+x.obj_name+"."+str(prop))+"_i" +", "+str(cval.imag) + ", " + str(t) +"]"  )
                                
                            else:
                                self.logger.info("[*] Not a number: "+str(val) )
                            #set the value at the end of the loop.
                            x.params[prop] = result
                            
                            
    def setup_gl_objects(self):
        gpm_conf = ConfigParser.RawConfigParser()
        try:
            gpm_conf.readfp(io.BytesIO(self.gridpotmodel))
        except Exception:
            print "Error reading the grid pot model from GridLAB-D"
            self.logger.info("Error reading the grid pot model from GridLAB-D")
            raise
            exit(0)
        for self.conpot_name in gpm_conf.sections(): # parse each section!
            for scada in gpm_conf.options(self.conpot_name):
                self.logger.info("[*] object type is: " + str(scada))
                if scada == "switch":
                    x = GL_SWITCH(self.gridlabd_ip, self.gridlabd_port, gpm_conf.get(self.conpot_name, scada), self.conpot_name)
                    self.SCADA_objects.append(x)
                elif scada == "transformer":
                    x = GL_TRANSFORMER(self.gridlabd_ip, self.gridlabd_port,  gpm_conf.get(self.conpot_name, scada), self.conpot_name)
                    self.SCADA_objects.append(x)
                elif scada == "regulator":
                    x = GL_REGULATOR(self.gridlabd_ip, self.gridlabd_port,  gpm_conf.get(self.conpot_name, scada), self.conpot_name)
                    self.SCADA_objects.append(x)
                #keep adding more as we go
        

    def initialize(self):
        request = 'http://' + self.gridlabd_ip + ':' + str(self.gridlabd_port) + '/output/' + self.gridpotmodel_file
        self.logger.info( request )
        response = urllib2.urlopen(request)
        self.gridpotmodel = response.read()
        self.logger.info( self.gridpotmodel )
        if self.gridpotmodel != None:
            self.setup_gl_objects()
        else:
            print "Could not get the .GPM model from GridLAB-D"
            self.logger.info("[!] Could not get the .GPM model from GridLAB-D")
            exit(0)
        
        self.poll_gridlabd()
        # end iniitialize

def main(argv=None):
    gpf = GridPotFeeder()
    gpf.initialize()

if __name__ == "__main__":
    main()        
