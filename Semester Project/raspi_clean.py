import time
import threading
import sys
import trace
import board
import neopixel
from adafruit_servokit import ServoKit
import pythonosc
from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import osc_server
import random




#raspi ip
ip = "192.168.0.102"
fromWekinator = 12000
state = 0
raw_state = 0

#LED strip on pin 18
pixel_pin = board.D18
num_pixels = 9
ORDER = neopixel.RGB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER)

def filter_handler(address, *args):
    global raw_state
    raw_state = int(args[0])
        
dispatcher = Dispatcher()
dispatcher.map("/wek/outputs", filter_handler)
server = osc_server.ThreadingOSCUDPServer((ip, fromWekinator), dispatcher)

# thread for the osc server
def start_server(ip, port):
    global server
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    threading.Thread()


start_server(ip, fromWekinator)

def toyMove(moveEvent):
    x = 0
    print("toymove")
    while True:
        moveEvent.wait()
        if(x%2==0):
            kit.servo[0].angle = random.randint(100,170)
            time.sleep(0.1)
            kit.servo[1].angle = random.randint(100,170)
            time.sleep(0.1)
            kit.servo[2].angle = random.randint(100,170)
            time.sleep(0.1)
            kit.servo[3].angle = random.randint(100,170)
            time.sleep(0.4)
            x=x+1
        else:
            kit.servo[0].angle = random.randint(10,100)
            time.sleep(0.1)
            kit.servo[1].angle = random.randint(10,100)
            time.sleep(0.1)
            kit.servo[2].angle = random.randint(10,100)
            time.sleep(0.1)
            kit.servo[3].angle = random.randint(10,100)
            time.sleep(0.4)
            x=x+1
        

def ledNormal(ledEvent):
    while True:
        ledEvent.wait()
        pixels.fill((255, 255, 255))
        pixels.show()
        time.sleep(0.3)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.3)
        
def ledP():
    kit.servo[0].angle = 170
    #time.sleep(0.1)
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.5)
    kit.servo[0].angle = 10
    pixels.fill((255, 0, 255))
    pixels.show()
    time.sleep(0.5)
    kit.servo[0].angle = 170
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.5)
    pixels.fill((255, 0, 255))
    pixels.show()
    time.sleep(0.5)
        

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

for i in range(4):
    kit.servo[i].set_pulse_width_range(1000, 2000)



moveEvent = threading.Event()
moveThread = threading.Thread(target=toyMove,args=(moveEvent,))
moveThread.start()
ledEvent = threading.Event()
ledThread = threading.Thread(target=ledNormal,args=(ledEvent,))
ledThread.start()
moveEvent.clear()
ledEvent.clear()
pixels.fill((0, 0, 0))
pixels.show()

while True:
    if(state != raw_state):
        state = raw_state
        print(state)
    
        #state 1 = no face
        #state 2 = voice recog in process
        #state 3 = positive voice
        #state 4 = have face
        if(state == 1):
            print("no face")
            while(raw_state == 1):
                moveEvent.set()
                ledEvent.set()
        elif(state == 4):
            print("yes face")
            pixels.fill((0, 0, 0))
            pixels.show()
            moveEvent.clear()
            ledEvent.clear()
            
        elif(state == 3):
            print("yes voice")
            pixels.fill((0, 0, 0))
            pixels.show()
            ledP()
        elif(state == 2):
            print("reading voice")
            moveEvent.clear()
            ledEvent.clear()
            pixels.fill((0, 0, 0))
            pixels.show()
            time.sleep(1)
            pixels.fill((255, 0, 255))
            pixels.show()
            
        


