import cv2
import imgutils

def old_detection(frame, cascade_upperbody, cascade_face):
        
    # Detect upperbodies in the frame and draw a green rectangle around it, if found
    (rects_upperbody, frame) = imgutils.detect_pattern(frame, cascade_upperbody, (60,60))
    frame = imgutils.box(rects_upperbody, frame)
    rects_face = [];
    decision = False;
    # Search for upperbodies!
    if len(rects_upperbody) > 0:
    
        # For each upperbody detected, search for faces! (Removes false positives)
        for x, y, w, h in rects_upperbody:
            frame_crop = frame[y:h, x:w];
            (rects_face, frame_crop) = imgutils.detect_pattern(frame_crop, cascade_face, (25,25))
            
            # For each face detected, make some drawings around it
            for xf, yf, wf, hf in rects_face:
            
                xf += x;
                yf += y;
                wf += x;
                hf += y;
                
                #cv2.circle(frame, ((w+x)/2, (h+y)/2), 10, (255,0,0), thickness=1, lineType=8, shift=0)
                #cv2.circle(frame, (wf, hf), 10, (0,0,255), thickness=1, lineType=8, shift=0)
                
                frame = imgutils.box([[xf, yf, wf, hf]], frame, (0, 0, 255))
    
    if len(rects_face) > 0:
        decision = True;
    
    return frame, decision


# based on a tutorial from http://www.pyimagesearch.com/
def motion_detection(frame, first_frame, min_area=200):
 
    decision = False

    # resize the frame, convert it to grayscale, and blur it
    #frame = imgutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
 
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < min_area:
            continue
 
        # compute the bounding box for the contour, draw it on the frame and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        decision = True

    return frame, decision