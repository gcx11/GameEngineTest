#!/usr/bin/env python3

import pygame

pygame.init()


class Game:

    def __init__(self, window_width, window_height, fps, title="Platformer"):
        """
        Basic setting for game.
        Parameters:
        window width, window height, FPS, pixel size and title
        """
        self.fps_clock = pygame.time.Clock()
        self.window_width = window_width
        self.window_height = window_height
        self.fps = fps
        self.screen = pygame.display.set_mode((self.window_width,
                                               self.window_height))
        pygame.display.set_caption(title)
        # user defined values


game = Game(1000, 600, 60)
