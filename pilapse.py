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
FOCUS = 18 #Green, pin 7 right
SHUTTER = 23 #Purple, pin 6 right

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
    print "Focussing Camera"
    GPIO.output(FOCUS, GPIO.HIGH)    
    return True
  
# This function is used to de-focus the camera
def blur():
    global FOCUS
    print "De-Focussing Camera"
    GPIO.output(FOCUS, GPIO.LOW)
    return True
  
# We also need to be able to trigger the shutter as needed  
def shutter(seconds_as_float=0.5):
    global SHUTTER
    print "Triggering the shutter of the Camera"
    GPIO.output(SHUTTER, GPIO.HIGH)
    print "Holding trigger for " + str(seconds_as_float) + " seconds"
    time.sleep(float(seconds_as_float))
    GPIO.output(SHUTTER, GPIO.LOW)
    return True

# To take the photo we need to do some things
def take_photo(focus_time=3, shutter_time=0.5):
    focus()
    time.sleep(float(focus_time))
    shutter(shutter_time)
    blur()
    return True


# Start the SimpleHTTPServer up and look for actions, otherwise server the remote page
class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        dir(self)
        GET = parse_qsl(urlparse(self.path)[4])
        if self.path.find("?") > 0:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            
            # Loop through the GET variables and create a set of variables
            for item in GET:                
                exec "%s = '%s'" % item
            
            # Check if at least an action is provided
            if 'action' in locals():
                
                # Is a command provided?
                if action == 'focus':
                    focus_time = 3
                    if 'ft' in locals():
                        focus_time = ft
                        
                    focus()
                    time.sleep(float(focus_time))
                    blur()
                    self.wfile.write('Focus completed')
                 
                # The take_photo action was provided   
                if action == 'take_photo':
                    shutter_speed = 0.5
                    focus_time = 3
                    
                    # Check if the additional info has been provided
                    if 'tv' in locals():
                        shutter_speed = tv
                    
                    if 'ft' in locals():
                        focus_time = ft
                    
                    # Taken the actual photo    
                    take_photo(focus_time, shutter_speed)
                    self.wfile.write('Photo taken')
                    
            
            # Not action provided, give an error
            else:
                self.wfile.write('ERROR: No action provided') 
        
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
