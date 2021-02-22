import pyaudio
import numpy as np

import cv2
import dlib
import pythonosc
from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc import osc_server
import threading


ip = "127.0.0.1"
fromWekinator = 12000

toWekinatorPort = 6448
client = SimpleUDPClient(ip, toWekinatorPort)  # Create client

# Load the detector
detector = dlib.get_frontal_face_detector()

# Load the predictor
predictor = dlib.shape_predictor("D:/Old_Schoolworks/Y4S2/interactive/RM3/shape_predictor_68_face_landmarks.dat")

level = 127
state = 0

# read the image
cap = cv2.VideoCapture(0)

def nothing(x):
    pass
cv2.namedWindow('face')
cv2.createTrackbar('Smily','face',0,255,nothing)
cv2.setTrackbarPos('Smily', 'face', state)

#-----------------------------------
# handling OSC
#this handles only two categories out of wekinator!!!
def filter_handler(address, *args):
    global state
    if int (args[0]) == 1 :
       state = 0
    else:
       state = 1


dispatcher = Dispatcher()
dispatcher.map("/wek/outputs", filter_handler)
server = osc_server.ThreadingOSCUDPServer((ip, fromWekinator), dispatcher)
print("Starting Server")
print("Serving on {}".format(server.server_address))


#thread for the osc server
def start_server(ip, port):
    global server
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    threading.Thread()

start_server(ip,fromWekinator)

#-----------------------------------


p = pyaudio.PyAudio()


#this plays frequencies, quick way to get a sound feeback
#one issue is that the streaming of the sound is BLOCKING, ie, nothing else happens while it plays

volume = 0.2    # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 0.1   # in seconds, may be float
f = 1000.0        # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

while (True):
    _, frame = cap.read()

    frame = cv2.resize(frame, (640, 480))
    # Convert image into grayscale
    gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
    
    # Use detector to find landmarks
    faces = detector(gray)

    for face in faces:
        x1 = face.left()  # left point
        y1 = face.top()  # top point
        x2 = face.right()  # right point
        y2 = face.bottom()  # bottom point

        # Create landmark object
        landmarks = predictor(image=gray, box=face)

        def normx(val):
            return (val - x1) / (x2-x1)
        def normy(val):
            return (val - y1) / (y2-y1)

        msg=[]
        msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
        # Loop through all the points
        for n in range(0,68):

            x = landmarks.part(n).x
            y = landmarks.part(n).y

            # Draw a circle
            cv2.circle(img=frame, center=(x, y), radius=2, color=(0, 255, 0), thickness=-1)

            # add the feature to the message
            msg.add_arg( normx(landmarks.part(n).x))
            msg.add_arg( normy(landmarks.part(n).y))

        # send the aggregated positions of all 68 features
        # this is 136 float numbers in a message
        msg=msg.build()
        client.send(msg)

        w = x2-x1
        h = y2-y1



    # Use detector to find landmarks
    faces = detector(gray)

    #this ticks up & down depending on the smile
    #circle feedback on the smile presence
    if state == 1:
        frame=cv2.circle(frame,(100,100), 30, (0,255,0), -1)
        level += 1
        if level > 255:
            level = 255
    else:
        frame=cv2.circle(frame, (100, 100), 30, (0, 0, 255), -1)
        state == 0
        level -= 1
        if level < 0:
            level = 0

    cv2.setTrackbarPos('Smily', 'face', level)

    f = level * 10 + 100.0
    # generate samples, note conversion to float32 array
    samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)

    stream.write(volume*samples)

    # show the image
    cv2.imshow('face', mat=frame)

    # Exit when escape is pressed
    if cv2.waitKey(delay=1) == 27:
        break

server.shutdown()
stream.stop_stream()
stream.close()
p.terminate()
cv2.destroyAllWindows()