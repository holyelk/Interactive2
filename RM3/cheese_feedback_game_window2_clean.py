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


level = 127
state = 0
stabalizer_counter = 0

# -----------------------------------
# handling OSC

def filter_handler(address, *args):
    global state
    global stabalizer_counter

    stabalizer_counter += 1
    if (stabalizer_counter % 3 == 0):
        state = int(args[0])





dispatcher = Dispatcher()
dispatcher.map("/wek/outputs", filter_handler)
server = osc_server.ThreadingOSCUDPServer((ip, fromWekinator), dispatcher)
print("Starting Server")
print("Serving on {}".format(server.server_address))


# thread for the osc server
def start_server(ip, port):
    global server
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    threading.Thread()


start_server(ip, fromWekinator)

# -----------------------------------

# Creating a window screen
wn = turtle.Screen()
wn.title("Snake Game")
wn.bgcolor("#222222")
# the width and height can be put as user's choice
wn.setup(width=1000, height=800)
wn.tracer(0)

# head of the snake. Size is 20x20
head = turtle.Turtle()
head.shape("square")
head.color("orange")
head.penup()
head.goto(0, 0)
head.direction = "Stop"

# food in the game
food = turtle.Turtle()
colors = random.choice(["#FFFFFF"])
shapes = random.choice(["circle"])
food.speed(0)
food.shape(shapes)
food.color(colors)
food.penup()
food.goto(0, 100)

pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 300)
pen.write("Score : 0 High Score : 0", align="center",
          font=("candara", 24, "bold"))


# assigning key directions
def goup():
    if head.direction != "down":
        head.direction = "up"


def godown():
    if head.direction != "up":
        head.direction = "down"


def goleft():
    if head.direction != "right":
        head.direction = "left"


def goright():
    if head.direction != "left":
        head.direction = "right"


def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y+20)
    if head.direction == "down":
        y = head.ycor()
        head.sety(y-20)
    if head.direction == "left":
        x = head.xcor()
        head.setx(x-20)
    if head.direction == "right":
        x = head.xcor()
        head.setx(x+20)


segments = []

# --------------

try:
    while True:
        
        if state == 1:
            goup()

        elif state == 2:
            godown()

        elif state == 3:
            goleft()

        elif state == 4:
            goright()

        else:
            pass

        wn.update()
        if head.xcor() > 490 or head.xcor() < -490 or head.ycor() > 390 or head.ycor() < -390:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "Stop"
            colors = random.choice(["#FFFFFF"])
            shapes = random.choice(["circle"])
            for segment in segments:
                segment.goto(1000, 1000)
            segments.clear()
            score = 0
            delay = 0.1
            pen.clear()
            pen.write("Score : {} High Score : {} ".format(
                score, high_score), align="center", font=("candara", 24, "bold"))

        if head.distance(food) < 20:
            x = random.randint(-470, 470)
            y = random.randint(-370, 370)
            food.goto(x, y)

            # Adding segment
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("orange")  # tail colour
            new_segment.penup()
            segments.append(new_segment)
            delay -= 0.001
            score += 10
            if score > high_score:
                high_score = score
            pen.clear()
            pen.write("Score : {} High Score : {} ".format(
                    score, high_score), align="center", font=("candara", 24, "bold"))
            # Checking for head collisions with body segments
        for index in range(len(segments)-1, 0, -1):
            x = segments[index-1].xcor()
            y = segments[index-1].ycor()
            segments[index].goto(x, y)
        if len(segments) > 0:
            x = head.xcor()
            y = head.ycor()
            segments[0].goto(x, y)
        move()
        for segment in segments:
            if segment.distance(head) < 20:
                time.sleep(1)
                head.goto(0, 0)
                head.direction = "stop"
                colors = random.choice(["#FFFFFF"])
                shapes = random.choice(["circle"])
                for segment in segments:
                    segment.goto(1000, 1000)
                segment.clear()

                score = 0
                delay = 0.1
                pen.clear()
                pen.write("Score : {} High Score : {} ".format(
                        score, high_score), align="center", font=("candara", 24, "bold"))
        time.sleep(delay)
except:

    server.shutdown()
    wn.mainloop()


