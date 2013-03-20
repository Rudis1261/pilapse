#!/usr/bin/env python
import SocketServer, SimpleHTTPServer, subprocess, os, commands, time
from urlparse import urlparse, parse_qsl
import RPi.GPIO as GPIO

# Change the PWD to this location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Variables (Constants)
PORT = 80
IP = ''

# Which pin is which?
FOCUS = 18
SHUTTER = 23

# Set the GPIO mode appropiately
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set the Pins up for their use
GPIO.setup(FOCUS, GPIO.OUT)
GPIO.setup(SHUTTER, GPIO.OUT)

# Pull them low to be safe
GPIO.output(FOCUS, GPIO.LOW)
GPIO.output(SHUTTER, GPIO.LOW)

# The function responsible to initiate the focus
def focus():
    global FOCUS
    GPIO.output(FOCUS, GPIO.HIGH)
    return True
  
# This function is used to de-focus the camera
def blur():
    global FOCUS
    GPIO.output(FOCUS, GPIO.LOW)
    return True
  
# We also need to be able to trigger the shutter as needed  
def shutter(seconds_as_float=0.5):
    global SHUTTER
    GPIO.output(SHUTTER, GPIO.HIGH)
    time.sleep(seconds_as_float)
    GPIO.output(SHUTTER, GPIO.LOW)
    return True


# Start the SimpleHTTPServer up and look for actions, otherwise server the remote page
class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        PARSE = parse_qsl(urlparse(self.path)[4])
        if self.path.find("?") > 0:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            for (command, value) in PARSE:                
                exec "%s = %s" % (command, value)
                
            print ""
            print ""
            print action
            print seconds
            
            '''# Is a command provided?
            if action == 'action':
                
                # Is the action 
                if value == 'focus':
                    focus()
                    time.sleep(3)
                    blur()
                    
                if value == 'capture':
                    focus()
                    time.sleep(3)
                    shutter()
                    blur()
                
            
            # Not, sure give a 0 response
            else:
                self.wfile.write('0') 
            return
            '''
        
        # Otherwise render the page as per normal
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #dir listing

# Launch the server
try:
    httpd = SocketServer.ThreadingTCPServer((IP, PORT),CustomHandler)
    print 'Starting server on PORT:' + str(PORT) + ', use <Ctrl-C> to stop'
    httpd.serve_forever()
except KeyboardInterrupt:
    print " pressed. Closing server"
    httpd.shutdown()
