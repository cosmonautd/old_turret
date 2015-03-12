"""
Categorize and play sounds randomly, based on category.
"""
# coding: utf-8

import pygame
import random
import os

class Soundcat(object):
    """Categorize and play sounds randomly, based on category.

        A Soundcat object plays a random sound from a given category.
        In order to do this, the sounds from a specific category must
        be in the same directory. You can add a category to a Soundcat
        object with the add_category() method as in the example below,
        where all sound files are in /home/user/songs/hello.
        
        >>> import soundcat;
        >>> sound = soundcat.Soundcat();
        >>> sound.add_category("Hello", "/home/user/songs/hello");
        
        For randomly playing a sound from an existing category, using
        our example:
        
        >>> sound.play("Hello");

        Note: All audio files must be WAV.
        
        Attributes:
            No public attributes.
            
    """

    def __init__(self):
        """Soundcat constructor.
        
            Args:
                None.
                
            Returns:
                A Soundcat object.
            
            Raises:
                No information.
            
        """
        
        pygame.init()
        pygame.mixer.init()
        
        # A dictionary to connect the names of categories and its sounds
        self._categories = {};
    
    
    def quit(self):
        """Quits safely.
        
            This method should be called before ending the program.
            
            Args:
                None.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        pygame.mixer.quit()
    

    def add_category(self, category_name, directory):
        """Adds a category.
        
            Args:
                category_name: name of category.
                directory: full path to the location where sounds are 
                           stored.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        # Link category name and path
        self._categories[category_name] = directory;
    
    
    def play(self, category_name):
        """Randomly play a sound from the specified category.
        
            Args:
                category_name: name of category.
            
            Returns:
                Nothing.
            
            Raises:
                No information.
            
        """
        
        # Get all WAV files of specified category
        entries = os.listdir(self._categories[category_name]);
        sounds = [];
        for entry in entries:
            if entry.endswith(".wav"):
                sounds.append(entry);
        
        # Load one of the files randomly and play it
        sound = pygame.mixer.Sound("/".join((self._categories[category_name], sounds[random.randrange(0, len(sounds))])));
        sound.play()
    
