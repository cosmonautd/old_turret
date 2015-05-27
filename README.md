# turret
People detection software written in Python, using openCV, based on turrets 
from the Portal games. It continuously scans the environment using image 
processing and saves frames where humans are detected.

Run with:

        $ python turret.py

[SAVE TO GOOGLE DRIVE IS CURRENTLY NOT WORKING. API DEPRECATED 27 May 2015]

This turret is able to save all people detections in a folder inside 
your Google Drive account. If you want this functionality, you'll have to 
input your login data when required. Also, as we're using a somewhat old
login method, Google will block this application by default. To enable
the Google Drive functionality, you'll have to visit this link
https://www.google.com/settings/security/lesssecureapps and enable access
for less secure apps.

Note: please, do not input your login data if you do not trust this program. 
Check our code, so you can trust it.

[SAVE TO GOOGLE DRIVE IS CURRENTLY NOT WORKING. API DEPRECATED 27 May 2015]

To use this project the following needs to be installed:

- OpenCV cv2:
    
    On Linux, OpenCV for Python will probably be in the repositories of your 
    distribution. In this case, use your package manager to install it.
    
    On Debian and derivatives (Ubuntu, Mint, elementary OS...):
    
        $ sudo apt-get install python-opencv

    Make sure your OpenCV version is at least 2.4, otherwise face recognition won't work!
    
    If your distro's repositories doesn't have an OpenCV version available, 
    try this PPA:
    
        $ sudo add-apt-repository ppa:alexei.colin/opencv
        $ sudo apt-get update
        $ sudo apt-get install python-opencv
    
    If this does not work and you don't use APT management tool, then try a 
    more hardcore method. A friend suggested the following tutorial:
    
    http://www.samontab.com/web/2014/06/installing-opencv-2-4-9-in-ubuntu-14-04-lts/
    
    
- Pygame:

    On Debian and derivatives (Ubuntu, Mint, elementary OS...)
    
        $ sudo apt-get install python-pygame
        

[SAVE TO GOOGLE DRIVE IS CURRENTLY NOT WORKING. API DEPRECATED 27 May 2015]

- gdata:

    For our purposes, gdata version must be 2.0.15 or above.

    On Debian and derivatives (Ubuntu, Mint, elementary OS...)
    
        $ sudo apt-get install python-gdata
        
    If the repositories of your distribution only have an older version of 
    gdata, you can try to install with python-pip:
    
        $ sudo pip install gdata
    
    Or you can download and install python-gdata from the following list:
    
    https://code.google.com/p/gdata-python-client/downloads/list

[SAVE TO GOOGLE DRIVE IS CURRENTLY NOT WORKING. API DEPRECATED 27 May 2015]

- GTK2:

    Our GUI uses GTK. If you don't have these for Python, use:
    
        $ sudo apt-get install python-gtk2 gtk2-engines-pixbuf
   


Note: This code has been tested in Ubuntu 14.04, Python 2.7.5 and OpenCV 2.4.8
