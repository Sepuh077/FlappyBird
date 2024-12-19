import os
import sys
import arcade

from src.constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
from src.game import GameView

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, True)
    arcade.set_window(window)
    window.menu = GameView(True, True, speed_up=1)
    window.show_view(window.menu)
    arcade.run()

if __name__ == "__main__":
    main()
