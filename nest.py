#!C:/Python27/python.exe

# nest.py -- a python interface to the Nest Thermostat
# by Scott M Baker, smbaker@gmail.com, http://www.smbaker.com/
#
# Usage:
#    'nest.py help' will tell you what to do and how to do it
#
# Licensing:
#    This is distributed unider the Creative Commons 3.0 Non-commecrial,
#    Attribution, Share-Alike license. You can use the code for noncommercial
#    purposes. You may NOT sell it. If you do use it, then you must make an
#    attribution to me (i.e. Include my name and thank me for the hours I spent
#    on this)
#
# Acknowledgements:
#    Chris Burris's Siri Nest Proxy was very helpful to learn the nest's
#       authentication and some bits of the protocol.

import urllib
import urllib2
import sys
from optparse import OptionParser
import cgitb


try:
   import json
except ImportError:
   try:
       import simplejson as json
   except ImportError:
       print "No json library available. I recommend installing either python-json"
       print "or simpejson."
       sys.exit(-1)

class Nest:
    def __init__(self, username, password, serial=None, index=0, units="F"):
        self.username = "yourUsername"
        self.password = "yourPassword"
        self.serial = serial
        self.units = units
        self.index = index

    def loads(self, res):
        if hasattr(json, "loads"):
            res = json.loads(res)
        else:
            res = json.read(res)
        return res

    def login(self):
        data = urllib.urlencode({"username": self.username, "password": self.password})

        req = urllib2.Request("https://home.nest.com/user/login",
                              data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4"})

        res = urllib2.urlopen(req).read()

        res = self.loads(res)

        self.transport_url = res["urls"]["transport_url"]
        self.access_token = res["access_token"]
        self.userid = res["userid"]

    def get_status(self):
        req = urllib2.Request(self.transport_url + "/v2/mobile/user." + self.userid,
                              headers={"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                                       "Authorization":"Basic " + self.access_token,
                                       "X-nl-user-id": self.userid,
                                       "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        res = self.loads(res)

        self.structure_id = res["structure"].keys()[0]

        if (self.serial is None):
            self.device_id = res["structure"][self.structure_id]["devices"][self.index]
            self.serial = self.device_id.split(".")[1]

        self.status = res

        #print "foo", res["structure"][self.structure_id]["away"]
        #print "res.keys", res.keys()
        #print "res[structure][structure_id].keys", res["structure"][self.structure_id].keys()
		#print "foo", res["structure"][self.structure_id].keys()["away"]
        #print "res[device].keys", res["device"].keys()
        #print "res[device][serial].keys", res["device"][self.serial].keys()
        #print "res[shared][serial].keys", res["shared"][self.serial].keys()

    def temp_in(self, temp):
        if (self.units == "F"):
            return (temp - 32.0) / 1.8
        else:
            return temp

    def temp_out(self, temp):
        if (self.units == "F"):
            return temp*1.8 + 32.0
        else:
            return temp
	
    def away_out(self):
        tempStructure = self.status["structure"][self.structure_id]["away"]
        self.print_value("away", tempStructure, 1, 1)
        #sys.stdout.write("away:\"")
        #sys.stdout.write(str(tempStructure))
        #sys.stdout.write("\"")
        
    def mode_out(self):
        self.print_value("mode", self.status["shared"][self.serial]["current_schedule_mode"], 1, 0)
        #sys.stdout.write("mode:\"")
        #sys.stdout.write()
        #sys.stdout.write("\"")
        
    def fan_out(self):
        self.print_value("fan_mode", self.status["shared"][self.serial]["fan_mode"], 1, 0)
        
    def set_out(self):
        self.print_value("set_temp", self.temp_out(self.status["shared"][self.serial]["target_temperature"]), 0, 0)
    
    def print_value(self, key, value, isString, isFirst):
        if (isFirst == 0):
            sys.stdout.write(",")
        sys.stdout.write("\"" + key + "\"")
        if (isString == 1):
            sys.stdout.write(":\"")
            sys.stdout.write(str(value))
            sys.stdout.write("\"")
        else:
            sys.stdout.write(":")
            sys.stdout.write(str(value))
        
    def show_status(self):
        shared = self.status["shared"][self.serial]
        device = self.status["device"][self.serial]

        allvars = shared
        allvars.update(device)

        sys.stdout.write("{")
        self.away_out()
        self.mode_out()
        self.fan_out()
        self.show_curtemp()
        self.set_out()
        
#        count = 0
#        for k in sorted(allvars.keys()):
#            if (count > 1):
#                sys.stdout.write(",")
#                sys.stdout.write(k + ":")
#                sys.stdout.write(str(allvars[k]))
#            count+=1
        sys.stdout.write("}"),
        
    def show_curtemp(self):
        temp = self.status["shared"][self.serial]["current_temperature"]
        temp = self.temp_out(temp)

        self.print_value("current_temperature", temp, 0, 0)
        #print "%0.1f" % temp

    def set_temperature(self, temp):
        temp = self.temp_in(temp)

        data = '{"target_change_pending":true,"target_temperature":' + '%0.1f' % temp + '}'
        req = urllib2.Request(self.transport_url + "/v2/put/shared." + self.serial,
                              data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                               "Authorization":"Basic " + self.access_token,
                               "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        print res

    def set_fan(self, state):
        data = '{"fan_mode":"' + str(state) + '"}'
        req = urllib2.Request(self.transport_url + "/v2/put/device." + self.serial,
                              data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                               "Authorization":"Basic " + self.access_token,
                               "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        print res

def create_parser():
   parser = OptionParser(usage="nest [options] command [command_options] [command_args]",
        description="Commands: fan temp",
        version="unknown")

   parser.add_option("-u", "--user", dest="user",
                     help="username for nest.com", metavar="USER", default=None)

   parser.add_option("-p", "--password", dest="password",
                     help="password for nest.com", metavar="PASSWORD", default=None)

   parser.add_option("-c", "--celsius", dest="celsius", action="store_true", default=False,
                     help="use celsius instead of farenheit")

   parser.add_option("-s", "--serial", dest="serial", default=None,
                     help="optional, specify serial number of nest thermostat to talk to")

   parser.add_option("-i", "--index", dest="index", default=0, type="int",
                     help="optional, specify index number of nest to talk to")


   return parser

def help():
    print "syntax: nest [options] command [command_args]"
    print "options:"
    print "   --user <username>      ... username on nest.com"
    print "   --password <password>  ... password on nest.com"
    print "   --celsius              ... use celsius (the default is farenheit)"
    print "   --serial <number>      ... optional, specify serial number of nest to use"
    print "   --index <number>       ... optional, 0-based index of nest"
    print "                                (use --serial or --index, but not both)"
    print
    print "commands: temp, fan, show, curtemp, curhumid"
    print "    temp <temperature>    ... set target temperature"
    print "    fan [auto|on]         ... set fan state"
    print "    show                  ... show everything"
    print "    curtemp               ... print current temperature"
    print "    curhumid              ... print current humidity"
    print
    print "examples:"
    print "    nest.py --user joe@user.com --password swordfish temp 73"
    print "    nest.py --user joe@user.com --password swordfish fan auto"

def main():
    #cgitb.enable()
    
    parser = create_parser()
    (opts, args) = parser.parse_args()

    if (len(args)==0) or (args[0]=="help"):
        #help()
        cmd = "show"
    else:
        cmd = args[0]

#    if (not opts.user) or (not opts.password):
#        print "how about specifying a --user and --password option next time?"
#        sys.exit(-1)

    if opts.celsius:
        units = "C"
    else:
        units = "F"

    n = Nest(opts.user, opts.password, opts.serial, opts.index, units=units)
    n.login()
    n.get_status()

    

    if (cmd == "temp"):
        if len(args)<2:
            print "please specify a temperature"
            sys.exit(-1)
        n.set_temperature(int(args[1]))
    elif (cmd == "fan"):
        if len(args)<2:
            print "please specify a fan state of 'on' or 'auto'"
            sys.exit(-1)
        n.set_fan(args[1])
    elif (cmd == "show"):
        n.show_status()
    elif (cmd == "curtemp"):
        n.show_curtemp()
    elif (cmd == "away"):
        n.away_out()
    elif (cmd == "curhumid"):
        print n.status["device"][n.serial]["current_humidity"]
    else:
        print "misunderstood command:", cmd
        print "do 'nest.py help' for help"

if __name__=="__main__":
    print "Content-Type: text/plain;charset=utf-8"
    print
    main()