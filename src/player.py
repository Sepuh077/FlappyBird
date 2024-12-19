import arcade
import numpy as np
import os
import time

from src.constants import IMAGES_DIR, SOUNDS_DIR, SCREEN_HEIGHT, SCREEN_WIDTH



class ScoreText(arcade.Text):
    def __init__(self, player, text='0', *args, **kwargs):
        super().__init__(text=text, *args, **kwargs)
        self.player = player

    def draw(self):
        if self.player.bot:
            self.text = self.player.name + ': ' + str(int(self.player.score / 10))
        else:
            self.text = self.player.name + ': ' + str(int(self.player.distance / 10))
        return super().draw()


class Player(arcade.Sprite):
    def __init__(self, name, bot=False, nn=None, *args, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm='Detailed')
        self.name = name
        self.start_pos = self.position
        self.default_texture = arcade.load_texture(
            os.path.join(IMAGES_DIR, "RJ_1.png")
        )
        self.jump_texture = arcade.load_texture(
            os.path.join(IMAGES_DIR, "RJ_2.png")
        )
        self.dead_texture = arcade.load_texture(
            os.path.join(IMAGES_DIR, "dead.png")
        )
        self.speed_up = 1
        self.jump_duration = 0.1
        self.jump_speed = 4
        self.bot = bot
        self.nn = None
        self.jump_sound = arcade.load_sound(os.path.join(SOUNDS_DIR, "jump.mp3"))
        self.jump_sound.play(volume=0)
        self.ms = 0
        self.jump_angle = 60
        if self.bot:
            self.nn = nn if nn else [np.random.rand(4, 6), np.random.rand(6, 1)]
        self.start()

    def start(self):
        self.texture = self.default_texture
        self.start_jump = None
        self.in_jump = False
        self.physics = arcade.PhysicsEnginePlatformer(self, gravity_constant=0.2 * (self.speed_up ** 2))
        self.score = 0
        self.distance = 0
        self.dead = False
        self.position = self.start_pos

    def get_distances_from_pipes(self, pipes):
        for i in range(0, len(pipes), 2):
            if pipes[i].center_x < self.center_x:
                continue
            return pipes[i].center_x - self.center_x, (pipes[i].top + pipes[i].bottom) / 2 - self.center_y
        return 0, 0

    def on_update(self, pipes=[], delta_time=1 / 60):
        self.physics.update()
        if self.in_jump and time.time() - self.start_jump > self.jump_duration:
            self.in_jump = False
            self.texture = self.default_texture

        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
            self.change_y = 0
        elif self.bottom < 0:
            self.bottom = 0
            self.change_y = 0
            self.physics.gravity_constant = 0
            self.die()
        if not self.dead:
            self.angle = max(-90, self.change_y / self.speed_up / self.jump_speed * self.jump_angle)
            self.distance += self.ms * delta_time
            if self.bot:
                dist_x, dist_y = self.get_distances_from_pipes(pipes)
                self.score = self.distance - abs(dist_y) * 0.1
                x = np.array([self.change_y / self.speed_up / 10, self.center_y / SCREEN_HEIGHT, dist_x / SCREEN_WIDTH, dist_y / SCREEN_HEIGHT])
                for w in self.nn:
                    x = x / x.max()
                    x = np.tanh(x @ w)

                if x.item() > 0.95:
                    self.jump()
        else:
            self.center_x -= self.ms * delta_time

    def die(self):
        self.dead = True
        self.texture = self.dead_texture

    def jump(self):
        if self.dead:
            return
        self.start_jump = time.time()
        self.in_jump = True
        self.physics.jump(self.jump_speed * self.speed_up)
        self.texture = self.jump_texture
        self.jump_sound.play(volume=0)
