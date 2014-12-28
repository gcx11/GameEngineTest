#!/usr/bin/env python3
import pygame
import random
import sys
from game import game


class GameObjectModel:

    def __init__(self):
        self.solid = True
        self.visible = True

    def render(self):
        ...

    def notify(self, event_name, *args, **kwargs):
        ...


class Button(GameObjectModel):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = pygame.Color("red")

    def render(self):
        game.screen.fill(self.color, (self.x, self.y, self.width, self.height))

    def notify(self, *args, **kwargs):
        if args[0] == "lmb_click":
            mouse_x = args[1]
            mouse_y = args[2]
            if (self.x <= mouse_x < self.x + self.width and
                self.y <= mouse_y < self.y + self.height):
                if self.color == pygame.Color("red"):
                    self.color = pygame.Color("green")
                else:
                    self.color = pygame.Color("red")
        elif args[0] == "tick":
            if not random.randint(0, 100):
                self.color = pygame.Color("blue")


class Block(GameObjectModel):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = pygame.Color("black")

    def render(self):
        game.screen.fill(self.color, (self.x, self.y, self.width, self.height))

    def notify(self, *args, **kwargs):
        pass


class Player(GameObjectModel):

    def __init__(self):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = pygame.Color("green")

    def render(self):
        game.screen.fill(self.color, (self.x, self.y, self.width, self.height))

    def check_collision(self, obj):
        if (obj.x <= self.x <= obj.x + obj.width or obj.y <= self.x + self.width <= obj.x + obj.width and
            obj.y <= self.y <= obj.y + obj.height or obj.y <= self.y + self.height <= obj.y + obj.height):
            return True
        else:
            return False

    def collide(self, obj):
        if self.check_collision(obj):
            pass

    def notify(self, *args, **kwargs):
        if args[0] == "tick":
            for obj in world.objects:
                if isinstance(obj, Block):
                    self.collide(obj)

class World:

    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    def render(self):
        for game_object in self.objects:
            if game_object.visible:
                game_object.render()

world = World()


class EventBase:

    def __init__(self, name):
        self.name = name
        self.listeners = []

    def __call__(self, *args, **kwargs):
        ...

    def update(self, *args, **kwargs):
        for listener in self.listeners:
            listener.notify(self.name, *args, **kwargs)

    def register(self, listener):
        self.listeners.append(listener)

    def unregister(self, listener):
        self.listeners.remove(listener)


class TickEvent(EventBase):

    def __init__(self):
        super().__init__("tick")


class LMBClickEvent(EventBase):

    def __init__(self):
        super().__init__("lmb_click")
        self.mouse_x = 0
        self.mouse_y = 0

    def __call__(self, *args, **kwargs):
        self.mouse_x = args[0]
        self.mouse_y = args[1]
        return self

    def update(self, *args, **kwargs):
        super().update(self.mouse_x, self.mouse_y)

TickEvent = TickEvent()
LMBClickEvent = LMBClickEvent()


class EventManager:

    def __init__(self):
        self.event_queue = []

    def process_normal(self):
        self.event_queue.append(TickEvent)

    def process_pygame(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.event_queue.append(LMBClickEvent(*event.pos))

    def update(self):
        for event in self.event_queue:
            event.update()
        self.event_queue.clear()

EventManager = EventManager()


class Engine:

    def __init__(self):
        self.world = world
        self.is_running = True

    def run(self):
        while self.is_running:
            game.screen.fill(pygame.Color("gray"))
            EventManager.process_normal()
            for event in pygame.event.get():
                EventManager.process_pygame(event)
            EventManager.update()
            world.render()
            pygame.display.update()
            game.fps_clock.tick(game.fps)


#########
#########
block_list = [Block(i*20, 500, 20, 20) for i in range(40)]
for block in block_list:
    world.add_object(block)
#########
#########
engine = Engine()
engine.run()
