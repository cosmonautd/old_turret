# coding: utf-8
# soundcat class
# Categorizes and play sounds randomly, based on category

import pygame
import random
import os

# Initialize pygame mixer
pygame.mixer.init()

class soundcat:

    # Class constructor
    def __init__(self):
        self.categories = {};   # Defines an empty dictionary to connect the names of categories and its sounds
    
    # Method that adds a category
    # Input : name of category and directory where its files are stored
    # Output: none, sounds are added to the category's dictionary
    def add_category(self, category_name, directory):
        self.categories[category_name] = directory;
    
    # Method that plays a category's sound randomly
    # Input : category's name
    # Output: none, a sound is selected from the category and played
    def play(self, category_name):
        entries = os.listdir(self.categories[category_name]);
        sounds = [];
        for entry in entries:
            if entry.endswith(".wav"):
                sounds.append(entry);
        sound = pygame.mixer.Sound(self.categories[category_name]+"/"+sounds[random.randrange(0, len(sounds))]);
        sound.play();
