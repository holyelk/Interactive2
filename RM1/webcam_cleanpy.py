import cv2
import numpy as np
import ctypes

darkness = 255
#avg is list of 20 to allow smooth light and dark changes
avg = [255]*20
trigger = 0
window_name = "window"

## get Screen Size
user32 = ctypes.windll.user32
screensize = (user32.GetSystemMetrics(0)), (user32.GetSystemMetrics(1))



# Creating the cascade objects
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# initialise the camera capture in OpenCV
video_capture = cv2.VideoCapture(0)



#determine the largest face to turn screen black(1/3 of screen size)
largestface = (user32.GetSystemMetrics(0)/3) * (user32.GetSystemMetrics(1)/3)

while True:
    W,H = screensize

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    #get video frame resolution
    height, width, depth = frame.shape

    #determine aspect ratio based on scale with screen size and frame size
    scaleWidth = float(W)/float(width)
    scaleHeight = float(H)/float(height)
    if scaleHeight>scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    
    #face detection
    process = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(process, 1.3, 5)

    ratio = 0.0

    #to detect only 1 face at a time
    i = 0


    for (x, y, w, h) in faces:
        i=i+1

        if (i == 1):
            #debuggin face rectangle
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            ratio = (w * h) / largestface

            # this multiply all pixels by the normalised ratio
            if (ratio >= 1.0):
                ratio = 1.0

            #Map a value of 0.1-0.45 to 0-200 to allow for the entire range of light and dark values to be used without going too far from the screen
            darkness = np.interp(ratio, [0.1,0.45], [200,0])

    
    #pop first from avg
    avg.pop(0)
    #adds new darkness value to the end of list
    avg.append(darkness)
    #get average so that no abrupt changes from last value
    darkness = sum(avg) / len(avg)
        


    np.multiply(frame, (1.0-ratio), out=frame, casting="unsafe")

    #normalize the frame and change the color at the same time
    cv2.normalize(frame, frame, 0, darkness, cv2.NORM_MINMAX)

    #flip frame for mirror
    frame = cv2.flip(frame, 1)

    #For resizing the frame to match aspect ratio
    newX,newY = frame.shape[1]*imgScale, frame.shape[0]*imgScale
    frame = cv2.resize(frame,(int(newX),int(newY)))
    
    #For black background
    my_img_1 = np.zeros((user32.GetSystemMetrics(1), user32.GetSystemMetrics(0), 1), dtype = "uint8")
    cv2.namedWindow("Background", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Background", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('Background', my_img_1)


    #auto center the window
    newCoordinate = (user32.GetSystemMetrics(0) - newX)/2
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, int(newCoordinate), 0)
    cv2.imshow(window_name, frame)

    #press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()