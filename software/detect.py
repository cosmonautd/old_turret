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