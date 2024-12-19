import os
import arcade
import arcade.color
import arcade.color
import arcade.color
import arcade.key
import time
import numpy as np
import gc

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH, IMAGES_DIR, Camera
from src.player import Player, ScoreText
from src.genetic_algorithm import GeneticAlgorithm


class Pipe(arcade.Sprite):
    def __init__(self, ms, *args, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm="Detailed")
        self.ms = ms

    def on_update(self, delta_time = 1 / 60):
        self.center_x -= delta_time * self.ms


class GameView(arcade.View):
    def __init__(self, alone=False, is_bots=False, speed_up=1):
        super().__init__()
        self.alone = alone
        self.is_bots = is_bots
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.wall_distance = SCREEN_WIDTH / 4
        self.hole_size = SCREEN_HEIGHT / 4
        self.pipe_image = os.path.join(IMAGES_DIR, 'pipe.png')
        self.genetic_algorithm = None
        self.score_texts = []
        self.players = arcade.SpriteList()
        self.pipes = arcade.SpriteList()
        self.speed_up = speed_up
        self.setup()

    def setup(self):
        gc.collect()
        self.score_texts.clear()
        self.players.clear()
        self.pipes.clear()
        if self.is_bots:
            if not self.genetic_algorithm:
                self.genetic_algorithm = GeneticAlgorithm(population_size=50)
                self.players.extend(self.genetic_algorithm.generate_population())
            else:
                self.players.extend(self.genetic_algorithm.update_population())
            
            self.population_text = arcade.Text(
                f'Population: {self.genetic_algorithm.population}',
                start_x=SCREEN_WIDTH / 2,
                start_y=SCREEN_HEIGHT * 0.8,
                color=arcade.color.BLACK,
                font_size=16,
                align='center',
                anchor_x='center',
                anchor_y='center',
                bold=True,
                width=200
            )
        elif not self.alone:
            self.players.append(Player(name='You', center_x=SCREEN_WIDTH / 4, center_y=SCREEN_HEIGHT / 2))
            self.players.append(Player(name='Bot', center_x=SCREEN_WIDTH / 4, center_y=SCREEN_HEIGHT / 2, bot=True))
        else:
            self.players.append(Player(name='You', center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 2))

        self.update_movespeed(ms=SCREEN_HEIGHT / 5)
        self.setup_score_texts()

    def update_movespeed(self, ms):
        self.ms = ms
        for pipe in self.pipes:
            pipe.ms = self.ms * self.speed_up

        for player in self.players:
            player.ms = self.ms * self.speed_up
            player.speed_up = self.speed_up

    def setup_score_texts(self):
        if self.alone or self.is_bots:
            for i, player in enumerate(self.players):
                self.score_texts.append(
                    ScoreText(
                        player=player,
                        start_x=5,
                        start_y=SCREEN_HEIGHT - 18 * (i + 1),
                        color=arcade.color.BLACK,
                        font_size=12,
                        align='left',
                        bold=True,
                        anchor_x='left',
                        anchor_y='center',
                        multiline=False,
                        width=100
                    )
                )

    def add_pipe(self):
        center = SCREEN_HEIGHT * (np.random.random() * 0.6 + 0.2)
        scale = SCREEN_WIDTH / 20 / 261
        pipe_bot = Pipe(
            texture=arcade.load_texture(self.pipe_image, 0, 0, 261, height=(center - self.hole_size / 2) / scale),
            scale=scale,
            center_x=SCREEN_WIDTH * 5 / 4,
            center_y=(center - self.hole_size / 2) / 2,
            ms=self.ms,
        )
        pipe_top = Pipe(
            texture=arcade.load_texture(self.pipe_image, 0, 0, 261, height=(SCREEN_HEIGHT - (center + self.hole_size / 2)) / scale),
            scale=scale,
            center_x=SCREEN_WIDTH * 5 / 4,
            center_y=(SCREEN_HEIGHT + center + self.hole_size / 2) / 2,
            ms=self.ms,
            angle=180
        )

        return [pipe_bot, pipe_top]

    def generate_pipes(self):
        if not self.pipes or self.pipes[-1].center_x <= SCREEN_WIDTH:
            self.pipes.extend(self.add_pipe())
        if self.pipes[0].center_x < -SCREEN_WIDTH / 4:
            self.pipes.pop(0)
            self.pipes.pop(0)

    def set_viewport(self, name=Camera.FULL, clear=True):
        if name == Camera.FULL:
            self.window.ctx.viewport = 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH, 0, SCREEN_HEIGHT
        elif name == Camera.LEFT:
            self.window.ctx.viewport = 0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH // 2, 0, SCREEN_HEIGHT
        elif name == Camera.RIGHT:
            self.window.ctx.viewport = SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT
            self.window.ctx.projection_2d = 0, SCREEN_WIDTH // 2, 0, SCREEN_HEIGHT
        if clear:
            self.clear()

    def on_draw(self):
        if self.alone or self.is_bots:
            self.set_viewport()
            self.pipes.draw()
            self.players.draw()
            for score_text in self.score_texts:
                score_text.draw()
            if self.is_bots:
                self.population_text.draw()
            return
        # left
        self.set_viewport(Camera.LEFT)
        self.pipes.draw()

        self.players[0].draw()

        # right
        self.set_viewport(Camera.RIGHT)
        self.pipes.draw()

        self.players[1].draw()

        self.set_viewport(clear=False)
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH / 30, SCREEN_HEIGHT, arcade.color.BLACK)


    def check_players_alive(self):
        for player in self.players:
            if not player.dead:
                return True
        return False

    def on_update(self, delta_time):
        for player in self.players:
            player.on_update(self.pipes, delta_time)

        self.players.update_animation(delta_time)
        self.players.update()

        self.pipes.on_update(delta_time)
        self.pipes.update()

        self.generate_pipes()

        for player in self.players:
            if player.collides_with_list(self.pipes):
                player.die()

        if not self.check_players_alive():
            self.setup()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            for player in self.players:
                if not player.bot:
                    player.jump()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for player in self.players:
                if not player.bot:
                    player.jump()
