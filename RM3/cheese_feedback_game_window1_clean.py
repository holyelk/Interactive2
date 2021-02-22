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

import turtle
import time
import random

delay = 0.1
score = 0
high_score = 0


ip = "127.0.0.1"
fromWekinator = 12000

toWekinatorPort = 6448
client = SimpleUDPClient(ip, toWekinatorPort)  # Create client

# Load the detector
detector = dlib.get_frontal_face_detector()

# Load the predictor
predictor = dlib.shape_predictor(
    "D:/Old_Schoolworks/Y4S2/interactive/RM3/shape_predictor_68_face_landmarks.dat")

level = 127
state = 0

# read the image
cap = cv2.VideoCapture(0)


def nothing(x):
    pass


cv2.namedWindow('face')

# --------------

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

        msg = []
        msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
        # Loop through all the points
        for n in range(0, 68):

            x = landmarks.part(n).x
            y = landmarks.part(n).y

            # add the feature to the message
            msg.add_arg(normx(landmarks.part(n).x))
            msg.add_arg(normy(landmarks.part(n).y))

        # send the aggregated positions of all 68 features
        # this is 136 float numbers in a message
        msg = msg.build()
        client.send(msg)

        w = x2-x1
        h = y2-y1

    # Use detector to find landmarks
    faces = detector(gray)

    frame = cv2.flip(frame, 1)

    cv2.imshow('face', mat=frame)

    # Exit when escape is pressed
    if cv2.waitKey(delay=1) == 27:
        break
    
cap.release()
cv2.destroyAllWindows()
