"""
A people detection turret. Will see everyone!
"""
# coding: utf-8

import cv2
import time
import datetime
import os
import thread
import signal
import sys
import soundcat
import save
import multiprocessing
import getpass
import argparse
import numpy
import gtk
import glib
import imgutils
import locale
import fps
import utils


# Parse command line arguments and set initial configuration

# Guarantee current locale is set to english, US, so month names are written in english always.
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

# Arguments parsing
parser = argparse.ArgumentParser(description="People detection turret. Detects people and optionally dispenses product")
parser.add_argument("-s", "--silent", help="Shut down the turret's sound modules.", action="store_true");
parser.add_argument("-g", "--googledrive", help="Save a copy of detections in a folder inside your Google Drive account", action="store_true");
parser.add_argument("-n", "--nogui", help="Doesn't show a graphical user interface.", action="store_true");
parser.add_argument("-r", "--rotate", type=int, help="Rotate camera input counterclockwise")

args = parser.parse_args();

# Soundcat object creation
# This object is responsible for categorizing sounds stored in sounds/, according to the situation
sound = soundcat.Soundcat();
sound.add_category("init", os.getcwd() + "/sounds/init");
sound.add_category("detection", os.getcwd() + "/sounds/detection");
sound.add_category("close", os.getcwd() + "/sounds/close");

# GoogleDocs class object creation
drive_ok = False;
if args.googledrive:
    print "\nThis turret is able to save all people detections in a folder inside your Google Drive account."
    print "If you want this functionality, please input your login data here. Else, leave both blank."
    print "As we're using a somewhat old login method, Google will block this application by default.\n"
    print "To enable Google Drive, visit:"
    print "https://www.google.com/settings/security/lesssecureapps"
    print "and enable access for less secure apps.\n"
    print "Please, do not input your login data if you do not trust this program. Check our code, so you can trust it.\n"
    gmail  = raw_input("Gmail account: ");
    passwd = getpass.getpass("Password: ");
    if gmail and passwd:
        print "Thank you. Activating..."
        upload = save.GoogleDocs(gmail, passwd);
        passwd = None;
        drive_ok = True;
        uploadqueue = save.UploadQueue(upload);
        # We use three threads to upload detections.
        thread.start_new_thread( uploadqueue.uploadloop, () )
        thread.start_new_thread( uploadqueue.uploadloop, () )
        thread.start_new_thread( uploadqueue.uploadloop, () )
    else:
        print "Ok. Blank data. Not connecting to Google."

# Width and height of the frames our turret will process
WIDTH  = 320;
HEIGHT = 240;
CV_WIDTH_ID  = 3;
CV_HEIGHT_ID = 4;

# Rotation of the frames our turret will process
if args.rotate: ROTATION = args.rotate;
else: ROTATION = None;

if args.silent: SILENT = True;
else: SILENT = False;

# Load Haar Cascade Classifiers for upperbody and face
# We use classifiers commonly found in opencv packages
cascade_upperbody = cv2.CascadeClassifier("haarcascades/haarcascade_mcs_upperbody.xml")
cascade_face = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt.xml")

# Frame counters, used to control our turret's talk timing and image saving speed
counter = 0     # Store total number of frames since start of execution
dcounter = 0    # Stores number of the last frame where a detection was made
LIMIT = 50      # Indicate limit of frames after the last detection in which we permit our turret to talk and save an image
last_sec_frames = 0;

# Build an FpsCounter object
fps_counter = fps.FpsCounter();

# Internet connection status
net_status = "OFF"

# Some functions to handle OS signals and GUI events

def sigint_handler(signum, instant):
    """Capture SIGINT signal and quit safely.
        
        Close all cameras, windows, say goodbye!
    """
    global SILENT;
    camera.release();
    fps_counter.quit();
    if not SILENT:
        sound.play("close")
        time.sleep(3)
    sound.quit()
    sys.exit()

# Update net connection status
def update_net_status():
    global net_status
    if utils.internet_on():
        net_status = "ON"
    else: 
        net_status = "OFF"
    return True;





class Gui:
    
    def __init__(self):
        if not args.nogui:
            # Create a GTK window, set icon, title, connect some functions to GUI elements
            self.MainWindow = gtk.Window()
            self.MainWindow.set_icon_from_file('icons/ic_camera_48px-128.png')
            self.MainWindow.set_title("Turret")
            self.MainWindow.set_resizable(False)
            self.MainWindow.connect("delete_event", self.delete_event)
            self.MainWindow.connect("destroy", gtk.main_quit)
            
            # Create a Box to contain all widgets
            self.MainBox = gtk.HBox(False, 0);
            self.MainWindow.add(self.MainBox)
            
            # Generate an initial black image and display it
            self.FrameArea = gtk.Image()
            pixbuf = gtk.gdk.pixbuf_new_from_array(numpy.zeros((HEIGHT,WIDTH,3), numpy.uint8), gtk.gdk.COLORSPACE_RGB, 8);
            pixbuf = pixbuf.scale_simple(WIDTH, HEIGHT, gtk.gdk.INTERP_BILINEAR);
            self.FrameArea.set_from_pixbuf(pixbuf)
            self.MainBox.pack_start(self.FrameArea, True, True, 0)
            
            separator = gtk.VSeparator()
            self.MainBox.pack_start(separator, False, True, 5)
            
            # Create a Box to contain the options panel
            self.PanelBox = gtk.VBox(False, 0)
            self.MainBox.pack_start(self.PanelBox, True, True, 0);
            
            separator = gtk.HSeparator()
            self.PanelBox.pack_start(separator, False, True, 5)
            
            # Frame size panel options
            self.FrameSizePanel = gtk.VBox(False, 0)
            self.PanelBox.pack_start(self.FrameSizePanel, False, True, 0);
            
            label = gtk.Label('Frame size')
            label.set_justify(gtk.JUSTIFY_LEFT)
            lalign = gtk.Alignment(0, 0.1, 0, 0.1)
            lalign.add(label)
            self.FrameSizePanel.pack_start(lalign, True, False, 0)
            
            self.FrameSizeOptions = gtk.HBox(False, 0)
            self.FrameSizePanel.pack_start(self.FrameSizeOptions, True, True, 0)
            
            button = gtk.RadioButton(None, "160x120")
            button.connect("toggled", self.on_framesizeoption_toggled, (160,120))
            self.FrameSizeOptions.pack_start(button, True, True, 0)

            button = gtk.RadioButton(button, "320x240")
            button.connect("toggled", self.on_framesizeoption_toggled, (320,240))
            button.set_active(True)
            self.FrameSizeOptions.pack_start(button, True, True, 0)

            button = gtk.RadioButton(button, "640x480")
            button.connect("toggled", self.on_framesizeoption_toggled, (640,480))
            self.FrameSizeOptions.pack_start(button, True, True, 0)
            
            separator = gtk.HSeparator()
            self.PanelBox.pack_start(separator, False, True, 5)
            
            
            # Frame rotation panel options
            self.FrameRotationPanel = gtk.VBox(False, 0)
            self.PanelBox.pack_start(self.FrameRotationPanel, False, True, 0);
            
            label = gtk.Label('Frame rotation')
            label.set_justify(gtk.JUSTIFY_LEFT)
            lalign = gtk.Alignment(0, 0.1, 0, 0.1)
            lalign.add(label)
            self.FrameRotationPanel.pack_start(lalign, True, False, 0)
            
            self.FrameRotationOptions = gtk.HBox(False, 0)
            self.FrameRotationPanel.pack_start(self.FrameRotationOptions, True, True, 0)
            
            button = gtk.RadioButton(None, "0")
            button.connect("toggled", self.on_framerotationoption_toggled, None)
            button.set_active(True)
            self.FrameRotationOptions.pack_start(button, True, True, 0)

            button = gtk.RadioButton(button, "90")
            button.connect("toggled", self.on_framerotationoption_toggled, 90)
            self.FrameRotationOptions.pack_start(button, True, True, 0)

            button = gtk.RadioButton(button, "180")
            button.connect("toggled", self.on_framerotationoption_toggled, 180)
            self.FrameRotationOptions.pack_start(button, True, True, 0)
            
            button = gtk.RadioButton(button, "270")
            button.connect("toggled", self.on_framerotationoption_toggled, 270)
            self.FrameRotationOptions.pack_start(button, True, True, 0)
            
            separator = gtk.HSeparator()
            self.PanelBox.pack_start(separator, False, True, 5)
            
            
            # More options panel
            self.MoreOptionsPanel = gtk.VBox(False, 0)
            self.PanelBox.pack_start(self.MoreOptionsPanel, False, True, 0);
            
            label = gtk.Label('More options')
            label.set_justify(gtk.JUSTIFY_LEFT)
            lalign = gtk.Alignment(0, 0.1, 0, 0.1)
            lalign.add(label)
            self.MoreOptionsPanel.pack_start(lalign, True, False, 0)
            
            self.MoreOptions = gtk.HBox(False, 0)
            self.MoreOptionsPanel.pack_start(self.MoreOptions, True, True, 0)
            
            button = gtk.CheckButton("Silent")
            button.connect("toggled", self.on_sound_option_toggled)
            button.set_active(SILENT)
            self.MoreOptions.pack_start(button, True, True, 0)

            button = gtk.CheckButton("Save to Drive")
            button.connect("toggled", self.on_save_to_drive_toggled)
            button.set_active(args.googledrive)
            self.MoreOptions.pack_start(button, True, True, 0)
            
            separator = gtk.HSeparator()
            self.PanelBox.pack_start(separator, False, True, 5)

            
            separator = gtk.VSeparator()
            self.MainBox.pack_start(separator, False, True, 5)
            
            # Show window
            self.MainWindow.show_all()
        
        # Make our frame capturing and detection function execute whenever there are no higher priority events in main GTK loop
        glib.timeout_add_seconds(5, update_net_status);
        glib.idle_add(self.set_frame);
    
    
    def on_framesizeoption_toggled(self, button, data):
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = data;
        camera.set(CV_WIDTH_ID, WIDTH);
        camera.set(CV_HEIGHT_ID, HEIGHT);
        
    def on_framerotationoption_toggled(self, button, data):
        global ROTATION
        ROTATION = data;
    
    def on_sound_option_toggled(self, button):
        global SILENT
        SILENT = button.get_active();
    
    def on_save_to_drive_toggled(self, button):
        pass;
    
    def delete_event(widget=None, *data):
        """Quit safely when GTK window is closed.
            
            Close all cameras, windows, say goodbye!
        """
        global SILENT
        camera.release();
        fps_counter.quit();
        if not SILENT:
            sound.play("close")
            time.sleep(3)
        sound.quit()
        return False
    
    
    # Detection and screen update function

    def set_frame(self):
        """Read a new frame from camera, process it, search for humans."""
        
        global counter, dcounter, LIMIT, last_sec_frames, WIDTH, HEIGHT, ROTATION, SILENT
        
        # Here, frames will be continuously captured and processed
        # Capture and apply some operations to captured frame before pattern detection
        ret ,frame = camera.read()                          # Capture a frame
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # Apply a grayscale filter
        
        # Rotate image if required
        if ROTATION:
            frame = imgutils.rotate(frame, ROTATION);
        
        # Detect upperbodies in the frame and draw a green rectangle around it, if found
        (rects_upperbody, frame) = imgutils.detect(frame, cascade_upperbody, (75,75))
        frame = imgutils.box(rects_upperbody, frame)
        
        # Get current time and date, writes it to image.
        now = datetime.datetime.now()
        cv2.putText(frame, str(now)[:19], (10,HEIGHT-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255))
        
        # Search for upperbodies!
        if len(rects_upperbody) > 0:
        
            # For each upperbody detected, search for faces! (Removes false positives)
            for x_1, y_1, x_2, y_2 in rects_upperbody:
                frame_crop = frame[y_1:y_2,x_1:x_2];
                (rects_face, frame_crop) = imgutils.detect(frame_crop, cascade_face, (40,40))
                
                # For each face detected, make some drawings around it
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
                    
                    frame = imgutils.box([coord], frame, (0, 0, 255))
        
            # Verify if it is time for our turret to speak and save a frame
            if len(rects_face) > 0 and counter - dcounter > LIMIT:
                dcounter = counter
                if not SILENT:
                    sound.play("detection")     # i see you, there you are
                now = datetime.datetime.now()
                if drive_ok:
                    thread.start_new_thread( save.save, (frame, now, uploadqueue) )   # another thread
                    #multiprocessing.Process( target=imgutils.save, args=(frame, now, uploadqueue)).start() # another process
                else:
                    thread.start_new_thread( save.save, (frame, now) )   # another thread
                    #multiprocessing.Process( target=imgutils.save, args=(frame, now)).start() # another process
        
        counter+=1;
        
        # Write current FPS on screen
        cv2.putText(frame, "FPS: {!s}".format(fps_counter.current_fps), (WIDTH-60,HEIGHT-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255))
        
        # If GUI is enabled, change image color model from BGR to RGB, convert to GTK compatible image, update frame.
        if not args.nogui:
            b, g, r = cv2.split(frame)
            frame_rgb = cv2.merge([r,g,b])
            pixbuf = gtk.gdk.pixbuf_new_from_array(frame_rgb, gtk.gdk.COLORSPACE_RGB, 8);
            self.FrameArea.set_from_pixbuf(pixbuf)
        
        # Inform our FPS counter that a frame has been processed
        fps_counter.update_frame_counter();
        print "\rFPS: {!s}".format(fps_counter.current_fps), "  INTERNET " + net_status + " ",
        sys.stdout.flush()
        
        return True;


# The main function!

if __name__ == '__main__':

    # The detector turret says Hello!
    if not SILENT:
        sound.play("init")
    
    # Activate capture of SIGINT (Ctrl-C)
    signal.signal(signal.SIGINT, sigint_handler)
    
    # Start a video capture from the first camera device found
    camera = cv2.VideoCapture(0)
    camera.set(CV_WIDTH_ID, WIDTH);
    camera.set(CV_HEIGHT_ID, HEIGHT);

    if not(camera == None):
        print "\nCamera is ready"
    print('Press Ctrl+C to finish')
    
    update_net_status();
    
    g = Gui();
    
    # Start GTK main loop
    gtk.main()
    
