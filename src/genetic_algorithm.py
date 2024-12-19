import numpy as np

from src.player import Player
from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH

class GeneticAlgorithm:
    def __init__(self, population_size=10):
        self.players = []
        self.population = 0
        self.size = population_size
        self.count = 0

    def new_individual(self, nn=None):
        self.count += 1
        return Player(name=f'Bot {self.count}', center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT / 2, bot=True, nn=nn)

    def generate_population(self):
        for i in range(self.size):
            self.players.append(
                self.new_individual()
            )
        self.population = 1
        return self.players

    def update_population(self):
        self.players = sorted(self.players, key=lambda player: player.score, reverse=True)
        for player in self.players[self.size // 2:]:
            player.kill()
            self.players.remove(player)
        parents_count = max(2, int(0.2 * self.size))
        mutations_count = max(3, len(self.players) - parents_count)

        for i in range(parents_count):
            self.players[i].start()

        for i in range(parents_count, parents_count + mutations_count):
            self.mutate(self.players[i])

        new_count = self.size - len(self.players)
        new_from_parents_count = max(2, int(new_count * 0.6))

        for i in range(new_from_parents_count):
            p1, p2 = np.random.choice(parents_count, 2, replace=False)
            self.players.append(self.cross(self.players[p1], self.players[p2]))

        new_random_count = self.size - parents_count - mutations_count - new_from_parents_count
        for _ in range(new_random_count):
            self.players.append(self.new_individual())

        self.population += 1

        return self.players

    def mutate(self, player: Player):
        nn = player.nn
        for i, w in enumerate(nn):
            w_flat = w.ravel()
            random_indices = np.random.choice(w.size, w.size // 2, replace=False)
            w_flat[random_indices] = np.random.random(w.size // 2)
            w = w_flat.reshape(w.shape)
            nn[i] = w
        player.nn = nn
        player.start()

    def cross(self, player1: Player, player2: Player):
        nn1 = player1.nn.copy()
        nn2 = player2.nn.copy()
        for i in range(len(nn1)):
            w1 = nn1[i].ravel()
            w2 = nn2[i].ravel()
            p = np.random.randint(0, w1.size // 3)
            random_indices = np.random.choice(w1.size, p, replace=False)
            for index in random_indices:
                w1[index] = w2[index]
            nn1[i] = w1.reshape(nn1[i].shape)

        return self.new_individual(nn1)
