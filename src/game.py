import os
import arcade
import arcade.color
import arcade.color
import arcade.key
import time
import numpy as np

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH, IMAGES_DIR, SOUNDS_DIR
from pyglet.math import Vec2


class Spike(arcade.Sprite):
    def __init__(self, ms=SCREEN_WIDTH / 20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textures = arcade.load_textures(
            os.path.join(IMAGES_DIR, 'cactus.png'),
            [(163 * (i % 3), 170 * (i // 3), 163, 170) for i in range(6)]
        )
        self.texture = textures[np.random.randint(0, len(textures) - 1)]
        self.scale = SCREEN_HEIGHT / 20 / self.height
        self.ms = ms

    def on_update(self, delta_time = 1 / 60):
        self.center_x -= delta_time * self.ms



class Bird(arcade.Sprite):
    def __init__(self, bot=False, nn=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_texture = arcade.load_texture(
            os.path.join(IMAGES_DIR, "RJ_1.png")
        )
        self.jump_texture = arcade.load_texture(
            os.path.join(IMAGES_DIR, "RJ_2.png")
        )
        self.texture = self.default_texture
        self.start_jump = None
        self.in_jump = False
        self.jump_duration = 0.1
        self.jump_speed = SCREEN_HEIGHT / 3
        self.g = SCREEN_HEIGHT / 1.2
        self.vertical_speed = 0
        self.bot = bot
        self.nn = None
        self.jump_sound = arcade.load_sound(os.path.join(SOUNDS_DIR, "jump.mp3"))
        self.jump_sound.play(volume=0)
        if self.bot:
            self.nn = nn if nn else [np.random.rand(2, 2), np.random.rand(2, 1)]

    def on_update(self, delta_time = 1 / 60):
        if self.in_jump and time.time() - self.start_jump > self.jump_duration:
            self.in_jump = False
            self.texture = self.default_texture
        self.center_y += self.vertical_speed * delta_time
        self.vertical_speed -= self.g * delta_time
        if self.bot:
            x = np.random.random((1, 2))
            for w in self.nn:
                x = x @ w

            if x.item() > 0.9:
                self.jump()


    def jump(self):
        self.start_jump = time.time()
        self.in_jump = True
        self.texture = self.jump_texture
        self.vertical_speed = self.jump_speed
        self.jump_sound.play()


class Wall(arcade.Sprite):
    def __init__(self, x, y, hole_length=SCREEN_HEIGHT / 5, wall_thikness=SCREEN_WIDTH / 20, ms=SCREEN_WIDTH / 10):
        self.hole_length = hole_length
        self.thikness = wall_thikness
        self.ms = ms
        super().__init__(center_x=x, center_y=y)

    def draw(self):
        arcade.draw_rectangle_filled(
            center_x=self.center_x,
            center_y=(self.center_y - self.hole_length / 2) / 2,
            width=self.thikness,
            height=self.center_y - self.hole_length / 2 - 50,
            color=arcade.color.GREEN,
        )
        arcade.draw_rectangle_filled(
            center_x=self.center_x,
            center_y=(SCREEN_HEIGHT + self.center_y + self.hole_length / 2) / 2,
            width=self.thikness,
            height=SCREEN_HEIGHT - (self.center_y + self.hole_length / 2),
            color=arcade.color.GREEN,
        )

    def on_update(self, delta_time = 1 / 60):
        self.center_x -= delta_time * self.ms


class GameView(arcade.View):
    def __init__(self, alone=False):
        super().__init__()
        self.alone = alone
        arcade.set_background_color(arcade.color.WHITE)
        self.wall_distance = SCREEN_WIDTH / 4
        self.ms = SCREEN_HEIGHT / 8
        self.walls = arcade.SpriteList()
        self.spikes = arcade.SpriteList()
        if not alone:
            self.left_camera = arcade.Camera(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
            self.left_camera.position = Vec2(0, 0)
            self.right_camera = arcade.Camera(SCREEN_WIDTH // 2, SCREEN_HEIGHT)
            self.right_camera.position = Vec2(SCREEN_WIDTH / 2, 0)
        else:
            pass
        self.setup()

    def setup(self):
        self.birds = arcade.SpriteList()
        if not self.alone:
            self.birds.append(Bird(center_x=SCREEN_WIDTH / 4, center_y=SCREEN_HEIGHT / 2))
            self.birds.append(Bird(center_x=SCREEN_WIDTH * 1 / 4, center_y=SCREEN_HEIGHT / 2, bot=True))
        else:
            self.birds.append(Bird(center_x=SCREEN_WIDTH * 3 / 4, center_y=SCREEN_HEIGHT / 2))
        self.setup_spikes()

    def setup_spikes(self):
        x = 0
        while x < SCREEN_WIDTH:
            self.spikes.append(
                Spike(center_x = x, center_y=85, ms=self.ms)
            )
            x += self.spikes[-1].width

    def generate_walls(self):
        if not self.walls or self.walls[-1].center_x <= SCREEN_WIDTH:
            self.walls.append(
                Wall(SCREEN_WIDTH * 5 / 4, SCREEN_HEIGHT * (np.random.random() * 0.6 + 0.2), ms=self.ms)
            )
        if self.walls[0].center_x < -SCREEN_WIDTH / 4:
            self.walls.pop(0)

    def generate_spikes(self):
        if self.spikes[-1].center_x <= SCREEN_WIDTH + self.spikes[-1].width:
            self.spikes.append(
                Spike(center_x = self.spikes[-1].center_x + self.spikes[-1].width, center_y=85, ms=self.ms)
            )
        if self.spikes[0].center_x < -SCREEN_WIDTH / 4:
            self.spikes.pop(0)

    def set_viewport(self, name='full', clear=True):
        if name == 'full':
            self.window.ctx.viewport = 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH, 0, SCREEN_HEIGHT
        elif name == 'left':
            self.window.ctx.viewport = 0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH // 2, 0, SCREEN_HEIGHT
        elif name == 'right':
            self.window.ctx.viewport = SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH // 2, 0, SCREEN_HEIGHT
        if clear:
            self.clear()

    def on_draw(self):
        # left
        self.set_viewport('left')
        self.walls.draw()
        for wall in self.walls:
            wall.draw()
        self.spikes.draw()
        self.birds[0].draw()

        # right
        self.set_viewport('right')
        self.walls.draw()
        for wall in self.walls:
            wall.draw()
        self.spikes.draw()
        self.birds[1].draw()

        self.set_viewport(clear=False)
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH / 30, SCREEN_HEIGHT, arcade.color.BLACK)

    def on_update(self, delta_time):
        self.birds.on_update(delta_time)
        self.birds.update_animation(delta_time)
        self.birds.update()
        self.walls.on_update(delta_time)
        self.spikes.on_update(delta_time)
        self.generate_walls()
        self.generate_spikes()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            for bird in self.birds:
                if not bird.bot:
                    bird.jump()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for bird in self.birds:
                if not bird.bot:
                    bird.jump()
