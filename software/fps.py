"""
Calculate frames per second.
"""
# coding: utf-8

import threading

class FpsCounter(object):
    """Calculate frames per second.

        An FpsCounter object is able to calculate how much frames
        per second were set in a video application. To use it, do
        the following:
        
        Create a FpsCounter object.
        
        >>> import soundcat;
        >>> fps_counter = fps.FpsCounter();
        
        Put the following line after a place in the code where you 
        finished setting a new frame:
        
        >>> fps_counter.update_frame_counter();
        
        Get the last second FPS with:
        
        >>> fps_counter.current_fps;

        
        Attributes:
            current_fps: actually, the last calculated FPS. This
                         variable is updated every second.
            
    """

    def __init__(self):
        """FpsCounter constructor.
        
            Args:
                None.
                
            Returns:
                A FpsCounter object.
            
            Raises:
                No information.
            
        """
        
        self._frame_counter = 0;
        self.current_fps = 0;
        self._update_fps_timer = threading.Timer(1, self._update_fps);
        self._update_fps_timer.start();
    
    
    def quit(self):
        """Quit safely.
        
            This method should be called before ending the program.
            
            Args:
                None.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        self._update_fps_timer.cancel();
    
    
    def update_frame_counter(self):
        """Update the current second frame count.
            
            Args:
                None.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        self._frame_counter+=1;
    
    
    def _update_fps(self):
        """Update FPS, clear frame count, schedule new run every second.
            
            Args:
                None.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        self.current_fps = self._frame_counter;
        self._frame_counter = 0;
        self._update_fps_timer = threading.Timer(1, self._update_fps);
        self._update_fps_timer.start();
    
