import cv2
import numpy
import pythonosc
from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import osc_server
import threading
import pigpio
import time
import random

ip = "192.168.0.102"
ipl = "192.168.0.101"
toWekinatorPort = 6448
fromWekinator = 12000
client = SimpleUDPClient(ip, toWekinatorPort)  # Create client

val = 0
pi = pigpio.pi()
pi.set_mode(26, pigpio.OUTPUT)

# initialise the face classifier
# locate the classifiers, different locations on Mac Os and RaspberryPi
# Creating the cascade objects
faceCascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# initialise the camera capture in OpenCV
video_capture = cv2.VideoCapture(0)

def nothing(x):
    pass

def filter_handler(address, *args):
    global val
    #print('weki classifier', args[0])
    #print(f"{address}: {args}")
    val = numpy.interp(int(args[0]*100),[0,100],[1800,1300])
    print(int(val))
    
dispatcher = Dispatcher()
dispatcher.map("/wek/outputs", filter_handler)
server = osc_server.ThreadingOSCUDPServer((ipl, fromWekinator), dispatcher)

def lookAround():
    pi.set_servo_pulsewidth(18,random.randrange(800,2200))
    time.sleep(0.1)

def blinker():
    #print("potato")
    pi.write(26, True)
    time.sleep(0.5)
    pi.write(26, False)
    time.sleep(0.5)

#thread for the osc server
def start_server(ip, port):
    global server
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    threading.Thread()

start_server(ip,fromWekinator)

blinkerT = threading.Thread()
timerT = threading.Thread()


while True:
    # start thread for random looking around
    if (not timerT.is_alive()):
        timerT = threading.Timer(3.0, lookAround)
        timerT.start()
    
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.flip(frame,1)

    scale_percent = 50  # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    process = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(process, 1.3, 5)
    
    
    i = 0
    for (x, y, w, h) in faces:
        timerT.cancel()
        i = i+1
        msg=[]
        msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
        cv2.rectangle(process, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
        centerx = x + (w/2)
        centery = y + (h/2)
        
        
        msg.add_arg(centerx)
        msg.add_arg(centery)
        
        msg=msg.build()
        client.send(msg)
        #set servo to value based on Wekinator interpolation
        pi.set_servo_pulsewidth(18, int(val))
        #Start thread for LED blinking
        if (not blinkerT.is_alive()):
            blinkerT = threading.Thread(target=blinker)
            blinkerT.start()
            
    
    cv2.imshow('Process', process)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()