# coding: utf-8
# Requires python-opencv and python-pygame (sudo apt-get install python-pygame python-opencv)

import cv2
import pygame
import time
import datetime
import os
import thread
import signal
import sys
import soundcat
import drive
import multiprocessing
import getpass
import argparse

# Arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--silent", help="Shut down the turret's sound modules.", action="store_true");
parser.add_argument("-g", "--googledrive", help="Save a copy of detections in a folder inside your Google Drive account", action="store_true");

args = parser.parse_args();

# pygame initialization
pygame.init()

# soundcat object creation
# This object is responsible for categorizing sounds stores in sounds/, according to the situation
# This makes our detector turret not so repetitive
sound = soundcat.soundcat();
sound.add_category("init", os.getcwd() + "/sounds/init");
sound.add_category("detection", os.getcwd() + "/sounds/detection");
sound.add_category("close", os.getcwd() + "/sounds/close");

# drive class object creation
drive_ok = False;
if args.googledrive:
    print "\nThis turret is able to save all people detections in a folder inside your Google Drive account."
    print "If you want this functionality, please input your login data here. Else, leave both blank."
    print "Note: please, do not input your login data if you do not trust this program. Check our code, so you can trust it.\n"
    gmail  = raw_input("Gmail account: ");
    passwd = getpass.getpass("Password: ");
    if gmail and passwd:
        print "Thank you. Activating..."
        upload = drive.drive(gmail, passwd);
        drive_ok = True;
    else:
        print "Ok. Blank data. Not connecting to Google."

# Width and heigth of the pictures our turret will process
width  = 320;
heigth = 240;

# Loads Haar Cascade Classifiers for upperbody and face
# We use classifiers commonly found in opencv packages
cascade_upperbody = cv2.CascadeClassifier("haarcascades/haarcascade_mcs_upperbody.xml")
cascade_face = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt.xml")

# Pattern detection functions for upperbody and face
# Input : an image
# Output: coordinates of the rectangle that contains the pattern described by the classifier
def detect_upperbody(img):
    min_rectangle = (75,75)   # Determines the minimum dimensions of the subset of the image where the pattern must be found
                                # Small values rise the range of vision of our turret, but processing may become slower
    rects = cascade_upperbody.detectMultiScale(img, 1.2, 3, cv2.cv.CV_HAAR_DO_CANNY_PRUNING, min_rectangle)

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img


def detect_face(img):
    min_rectangle = (40,40)
    
    rects = cascade_face.detectMultiScale(img, 1.2, 3, cv2.cv.CV_HAAR_DO_CANNY_PRUNING, min_rectangle)

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

# Function for drawing a rectangle over every recognized pattern
# Input : coordinates of the rectangle containing the recognized pattern (top-left and bottom-right), the image, a color indication
# Output: the image, properly marked
def box(rects, img, color):
    
    if color == 'green':
        c = (127,255,0);
    elif color == 'red':
        c = (0,0,255);
    
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), c, 2)
    return img

# Function for saving an image in a hierarchical structure inside the detected/ folder: year/month/day/image
#   Additionally saves the image using a similar structure inside a Google Drive account, if set.
# Input : an image and the current time
# Output: none
def save_img(img, time):
    if os.path.exists("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day)):
        cv2.imwrite("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", img)
    elif os.path.exists("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B')):
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day))
        cv2.imwrite("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", img)
    elif os.path.exists("detected/" + str(time.year)):
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B'))
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day))
        cv2.imwrite("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", img)
    elif os.path.exists("detected"):
        os.mkdir("detected/" + str(time.year))
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B'))
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day))
        cv2.imwrite("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", img)
    else:
        os.mkdir("detected")
        os.mkdir("detected/" + str(time.year))
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B'))
        os.mkdir("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day))
        cv2.imwrite("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", img)
    
    if drive_ok:
        upload_path = upload.get_path(time);
        upload.save_img("detected/" + str(time.year) + "/" + str(time.month) + "." + time.strftime('%B') + "/" + str(time.day) + "/" + str(time)[:19] + ".png", upload_path);

# Function for rotating an image 90º
# Input : an image
# Output: the image, properly rotated
def rotate(img):
    # Captures the dimensions of the image and computes it center
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    # rotates the image 90º
    M = cv2.getRotationMatrix2D(center, 90, 1.0)
    return cv2.warpAffine(img, M, (w, h))

# Function for capturing the signal SIGINT (Ctrl-C) and finishing the program
# Close all windows, says goodbye!
def signal_handler(signal, instant):
    cv2.destroyAllWindows()
    if not args.silent:
        sound.play("close")
        time.sleep(3)
    exit(0)


# Main program
if __name__ == '__main__':
    
    # The detector turret says Hello!
    if not args.silent:
        sound.play("init")
    
    # Activates the capture of SIGINT (Ctrl-C)
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to finish')
    
    # Starts a video capture from the first video device found on the computer
    # Video frames will be captured using the opencv object VideoCapture
    camera = cv2.VideoCapture(0)
    
    # Frame counters, used to control our turret's talk timing and image saving speed
    counter = 0     # Stores the total number of frames since start of execution
    dcounter = 0    # Stores the number of the last frame where a detection was made
    limit = 50      # Indicates the limit of frames after the last detection in which we permit our turret to talk and save an image
    
    # Main loop
    # Here, frames will be continuously captured and processed
    while 1:
        # Captures and apply some operations to the image before pattern detection
        (_,frame) = camera.read()                           # Captures a frame
        frame = cv2.resize(frame, (width, heigth))          # Resize the frame
        #frame = rotate(frame)                              # Rotates the frame (if camera is in a different orientation)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # Applies a grayscale filter
        
        # Detects upperbodies in the frame and draws a green rectangle around it, if found
        (rects_upperbody, frame) = detect_upperbody(frame)
        frame = box(rects_upperbody, frame, 'green')
        
        now = datetime.datetime.now()
        cv2.putText(frame, str(now.year) + "/" + str(now.month) + "/" + str(now.day) + "/" + str(now)[:19], (10,heigth-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255))
        
        if len(rects_upperbody) > 0:
        
            for x_1, y_1, x_2, y_2 in rects_upperbody:
                frame_crop = frame[y_1:y_2,x_1:x_2];
                (rects_face, frame_crop) = detect_face(frame_crop)
                
                for coord in rects_face:
                    x1 = coord[0]
                    y1 = coord[1]
                    x2 = coord[2]
                    y2 = coord[3]
                    coord[0] = x1 + x_1;
                    coord[1] = y1 + y_1;
                    coord[2] = x2 + x_1;
                    coord[3] = y2 + y_1;
                    
                    cv2.circle(frame, (coord[0],coord[1]), 10, (255,0,0), thickness=1, lineType=8, shift=0)
                    cv2.circle(frame, (coord[2],coord[3]), 10, (0,0,255), thickness=1, lineType=8, shift=0)
                    
                    frame = box([coord], frame, 'red')
        
            # Verifies if it is time for our turret to speak and save a frame
            if len(rects_face) > 0 and counter - dcounter > limit:
                dcounter = counter
                if not args.silent:
                    sound.play("detection")     # i see you, there you are
                now = datetime.datetime.now()
                thread.start_new_thread( save_img, (frame, now) )   # save_img() function is run in another thread
                #multiprocessing.Process( target=save_img, args=(frame, now)).start() # save_img() function in run in another process
        
        # Shows all frames in a window. Exits if ESC is pressed.
        cv2.imshow('People Detection Turret',frame)
        counter+=1
        if cv2.waitKey(1)==27:
            break
    
    # Close all windows
    cv2.destroyAllWindows()
    # Goodbye, says our detector turret
    if not args.silent:
        sound.play("close")
        time.sleep(3)
    
