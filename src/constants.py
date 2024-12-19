import arcade
import os


# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()
# SCREEN_WIDTH, SCREEN_HEIGHT = 400, 700
SCREEN_TITLE = "Flappy bird"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')

class Camera:
    LEFT = 'left'
    RIGHT = 'right'
    FULL = 'full'
