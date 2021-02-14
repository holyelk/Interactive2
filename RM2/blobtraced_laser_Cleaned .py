# Standard imports
import cv2
import numpy as np
import time
import ctypes
from pydub import AudioSegment
from pydub.playback import play
import threading
import keyboard
import argparse

def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    """Overlay img_overlay on top of img at the position specified by
    pos and blend using alpha_mask.

    Alpha mask must contain values within the range [0, 1] and be the
    same size as img_overlay.
    """

    x, y = pos

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha

    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])
                    



## get Screen Size
user32 = ctypes.windll.user32
screensize = (user32.GetSystemMetrics(0)), (user32.GetSystemMetrics(1))

#create Background Subtractor objects
backSub = cv2.bgsegm.createBackgroundSubtractorMOG()

#counter for duck
duck_counter = 0

#Get duck image in PNG
duck = cv2.imread('C:/Users/Bryan/Desktop/school/NTU/modules/y4s2/RM2/ducksmall.png', cv2.IMREAD_UNCHANGED)

#For black background
my_img_1 = np.zeros((user32.GetSystemMetrics(1), user32.GetSystemMetrics(0), 1), dtype = "uint8")
cv2.namedWindow("Background", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Background", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow('Background', my_img_1)

# resize image
scale_percent = 3 # percent of original size
width = int(duck.shape[1] * scale_percent / 100)
height = int(duck.shape[0] * scale_percent / 100)
dim = (width, height)

resized_duck = cv2.resize(duck, dim, interpolation = cv2.INTER_AREA)

#Get duck audio
song = AudioSegment.from_wav("C:/Users/Bryan/Desktop/school/NTU/modules/y4s2/RM2/ducksound_short.wav")

# initialise the camera capture in OpenCV
video_capture = cv2.VideoCapture(1)

#getting an image as background canvas...
ret, canvas = video_capture.read()
cv2.normalize(canvas, canvas, 0, 10, cv2.NORM_MINMAX)



while True:
    W,H = screensize

    # Capture frame-by-frame
    ret, img = video_capture.read()

    #get video frame resolution
    height, width, depth = img.shape

    #determine aspect ratio based on scale with screen size and frame size
    scaleWidth = float(W)/float(width)
    scaleHeight = float(H)/float(height)
    if scaleHeight>scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply Gaussian Blur
    thresh1 = cv2.GaussianBlur(gray, (5,5), sigmaX=4, sigmaY=4, borderType = cv2.BORDER_DEFAULT)

    #apply background subtractor
    fgMask = backSub.apply(thresh1)

    #Blob detector and params
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 80
    params.maxThreshold = 255
    params.filterByArea = True
    params.minArea = 100
    params.maxArea = 300
    params.blobColor = 255

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(fgMask)
    ret, img1 = cv2.threshold(fgMask, 255, 255, cv2.THRESH_BINARY)

    # Draw detected blobs keypoints
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(img1, keypoints, np.array([]), (0,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


    duck_counter = duck_counter + 1

    #To change the keypoints to ducks
    for keyPoint in keypoints:
        #To prevent audio lag every 2 add duck and audio
        if (duck_counter%2 == 0):
            x = keyPoint.pt[0]
            y = keyPoint.pt[1]
            s = keyPoint.size
            
            #Find number of threads
            threadsize = threading.enumerate()

            #Restrict number of threads
            if (len(threadsize) <= 10):
                t = threading.Thread(target=play, args=(song,))
                t.start()
            
            #Ducks
            overlay_image_alpha(im_with_keypoints,
                        resized_duck[:, :, 0:3],
                        (int(x), int(y)),
                        resized_duck[:, :, 3] / 255.0)
            



    #THIS WILL DRAW ALL THE KEYPOINTS FROM EVERY FRAME INTO THE CANVAS
    canvas = cv2.addWeighted(im_with_keypoints, 0.6, canvas, 1, 0.0 )

    #Full screen the window
    cv2.namedWindow("Canvas", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Canvas",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    # Show
    cv2.imshow("Canvas", canvas)

    #Quit 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
