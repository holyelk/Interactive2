import cv2
import mediapipe as mp
import pythonosc
from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc.udp_client import SimpleUDPClient
import threading
import time
import speech_recognition as sr


msg = []

avg = [255]*20

ip = "127.0.0.1"
toWekinatorPort = 6448
client = SimpleUDPClient(ip, toWekinatorPort)  # Create client

state = 0


def voiceFunc():
    # obtain audio from the microphone
    r = sr.Recognizer()
    global msg
    global state
    state = 11
    msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
    msg.add_arg(float(state))
    msg = msg.build()
    client.send(msg)
    msg = []
    msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 2000
        print("Say something!")
        audio = r.listen(source)
    # recognize speech using Google Speech Recognition
    try:
        if (r.recognize_google(audio) == "hello there"):
          print("Yes")
          msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
          state = 66
          msg.add_arg(float(state))
          msg = msg.build()
          client.send(msg)
          msg = []
          msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(e))



def main():
  mp_face_detection = mp.solutions.face_detection


  voiceThread = threading.Thread()
  # For webcam input:
  cap = cv2.VideoCapture(1)
  with mp_face_detection.FaceDetection(
          min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # Flip the image horizontally for a later selfie-view display, and convert
      # the BGR image to RGB.
      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      results = face_detection.process(image)



      # Prepare DrawingSpec for drawing the face landmarks later.
      mp_drawing = mp.solutions.drawing_utils
      drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

      # Draw the face detection annotations on the image.qq
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      if results.detections:
        for detection in results.detections:
          #wekinator
          msg = []
          msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
          state = 10
          msg.add_arg(float(state))
          location_data = detection.location_data
          #pop first from avg
          avg.pop(0)
          avg.append(location_data.relative_bounding_box.xmin)
          #0.03
          if (sum(avg) / len(avg)) <= 0.03:
            if (not voiceThread.is_alive()):
              voiceThread = threading.Thread(target=voiceFunc, args=[])
              voiceThread.start()
              time.sleep(5.0)
          mp_drawing.draw_detection(image, detection)
          msg = msg.build()
        client.send(msg)
      else:
        #wekinator
        msg = []
        msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
        state = 0
        msg.add_arg(float(state))
        msg = msg.build()
        client.send(msg)
      cv2.imshow('MediaPipe Face Detection', image)
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()


if __name__ == '__main__':
    main()
