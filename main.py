#!/usr/bin/env python3

import enum
import pygame
from pygame.locals import *
import random
import sys
from game import game


class GameCamera:

    def __init__(self, width, height):
        self.state = Rect(0, 0, width, height)
        self.level_width = 0
        self.level_height = 0

    def set_level_area(self, level_width, level_height):
        self.level_width = level_width
        self.level_height = level_height

    def apply(self, target):
        return target.x - self.state.x, target.y - self.state.y, target.width, target.height

    def update(self, target):
        self.state.center = target.rect.center
        if target.rect.x < (self.state.width - target.rect.width)/2:
            self.state.x = 0
        elif target.rect.x > self.level_width - (self.state.width + target.rect.width)/2:
            self.state.x = self.level_width - self.state.width
        if target.rect.y < (self.state.height - target.rect.height)/2:
            self.state.y = 0
        elif target.rect.y > self.level_height - (self.state.height + target.rect.height)/2:
            self.state.y = self.level_height - self.state.height


camera = GameCamera(800, 600)
camera.set_level_area(2000, 1000)


class GameObject(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = Rect(x, y, width, height)
        self.image = None
        self.solid = True
        self.visible = True

    def render(self):
        if camera.state.colliderect(self.rect):
            game.screen.blit(self.image, camera.apply(self.rect))

    def notify(self, event):
        pass


class Block(GameObject):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color("gray"))


class MovingBlock(GameObject):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color("gray"))
        self.distance = 10


class EntityState(enum.Enum):

        standing = 1
        walking_left = 2
        walking_right = 3
        jumping_up = 4
        jumping_left = 5
        jumping_right = 6
        falling_down = 7
        falling_left = 8
        falling_right = 9


class Entity(GameObject):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color("blue"))
        self.force = pygame.math.Vector2(0, 0)
        self.state = EntityState.standing

    def move_x(self):
        self.rect.x += self.force.x

    def move_y(self):
        self.rect.y += self.force.y

    def collide_x(self, block):
        if self.force.x < 0:
            self.rect.left = block.rect.right
        elif self.force.x > 0:
            self.rect.right = block.rect.left

    def collide_y(self, block):
        if self.force.y < 0:
            self.rect.top = block.rect.bottom
        elif self.force.y > 0:
            self.rect.bottom = block.rect.top

    def physic(self):
        self.set_force()
        self.move_x()
        for block in world.blocks:
            if self.rect.colliderect(block):
                self.collide_x(block)
        self.move_y()
        for block in world.blocks:
            if self.rect.colliderect(block):
                self.collide_y(block)


class Player(Entity):

    class KeyConfig:

        def __init__(self, key_up, key_left, key_right):
            self.key_up = key_up
            self.key_left = key_left
            self.key_right = key_right

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        KeyboardEvent.register(self)
        self.state = EntityState.falling_down
        self.key_config = Player.KeyConfig(pygame.K_w, pygame.K_a, pygame.K_d)
        # jump forces and constants
        self.jump_force = 3.5
        self.gravity_force = 0.5
        self.actual_jump_force = 0
        self.on_ground = False

    def notify(self, event):
        if event.name == "keyboard_event":
            # falling down
            if self.state == EntityState.falling_down:
                if self.on_ground:
                    self.actual_jump_force = 0
                    self.state = EntityState.standing
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.falling_left
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.falling_right
            # falling left
            elif self.state == EntityState.falling_left:
                if self.on_ground:
                    self.actual_jump_force = 0
                    self.state = EntityState.standing
                elif event.keyboard_dict.get(self.key_config.key_left) is False:
                    self.state = EntityState.falling_down
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.falling_right
            # falling right
            elif self.state == EntityState.falling_right:
                if self.on_ground:
                    self.actual_jump_force = 0
                    self.state = EntityState.standing
                elif event.keyboard_dict.get(self.key_config.key_right) is False:
                    self.state = EntityState.falling_down
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.falling_left
            # jumping up
            elif self.state == EntityState.jumping_up:
                if self.actual_jump_force <= 0:
                    self.actual_jump_force = 0
                    self.state = EntityState.falling_down
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.jumping_left
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.jumping_right
            # jumping left
            elif self.state == EntityState.jumping_left:
                if self.actual_jump_force <= 0:
                    self.actual_jump_force = 0
                    self.state = EntityState.falling_left
                elif event.keyboard_dict.get(self.key_config.key_left) is False:
                    self.state = EntityState.jumping_up
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.jumping_right
            # jumping right
            elif self.state == EntityState.jumping_right:
                if self.actual_jump_force <= 0:
                    self.actual_jump_force = 0
                    self.state = EntityState.falling_right
                elif event.keyboard_dict.get(self.key_config.key_right) is False:
                    self.state = EntityState.jumping_up
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.jumping_left
            # walking left
            elif self.state == EntityState.walking_left:
                if not self.on_ground:
                    self.state = EntityState.falling_left
                elif event.keyboard_dict.get(self.key_config.key_left) is False:
                    self.state = EntityState.standing
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.walking_right
            # walking right
            elif self.state == EntityState.walking_right:
                if not self.on_ground:
                    self.state = EntityState.falling_right
                elif event.keyboard_dict.get(self.key_config.key_right) is False:
                    self.state = EntityState.standing
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.walking_left
            # standing
            else:
                if not self.on_ground:
                    self.state = EntityState.falling_down
                elif event.keyboard_dict.get(self.key_config.key_up) is True:
                    self.actual_jump_force = self.jump_force
                    self.state = EntityState.jumping_up
                    self.on_ground = False
                elif event.keyboard_dict.get(self.key_config.key_left) is True:
                    self.state = EntityState.walking_left
                    self.on_ground = False
                elif event.keyboard_dict.get(self.key_config.key_right) is True:
                    self.state = EntityState.walking_right
                    self.on_ground = False

    def set_force(self):
        # falling down
        if self.state == EntityState.falling_down:
            self.force.x = 0
            self.force.y += self.gravity_force
        # falling left
        elif self.state == EntityState.falling_left:
            self.force.x = -5
            self.force.y += self.gravity_force
        # falling right
        elif self.state == EntityState.falling_right:
            self.force.x = 5
            self.force.y += self.gravity_force
        # jumping up
        elif self.state == EntityState.jumping_up:
            self.force.x = 0
            self.force.y -= self.actual_jump_force
            self.actual_jump_force -= self.gravity_force
        # jumping left
        elif self.state == EntityState.jumping_left:
            self.force.x = -5
            self.force.y -= self.actual_jump_force
            self.actual_jump_force -= self.gravity_force
        # jumping right
        elif self.state == EntityState.jumping_right:
            self.force.x = 5
            self.force.y -= self.actual_jump_force
            self.actual_jump_force -= self.gravity_force
        # walking left
        elif self.state == EntityState.walking_left:
            self.force.y = 0
            self.force.x = -5
        # walking right
        elif self.state == EntityState.walking_right:
            self.force.y = 0
            self.force.x = 5
        # standing
        else:
            self.force.x = 0
            self.force.y = 0

    def collide_x(self, block):
        if self.force.x < 0:
            self.state = EntityState.standing
            self.rect.left = block.rect.right
            self.force.x = 0
        elif self.force.x > 0:
            self.state = EntityState.standing
            self.rect.right = block.rect.left
            self.force.x = 0

    def collide_y(self, block):
        if self.force.y < 0:
            self.state = EntityState.falling_down
            self.rect.top = block.rect.bottom
            self.force.y = 0
        elif self.force.y > 0:
            self.on_ground = True
            self.force.y = 0
            self.state = EntityState.standing
            self.rect.bottom = block.rect.top

    def physic(self):
        self.set_force()
        self.move_x()
        for block in world.blocks:
            if self.rect.colliderect(block):
                self.collide_x(block)
        self.move_y()
        for block in world.blocks:
            if self.rect.colliderect(block):
                self.on_ground = False
                self.collide_y(block)


class HealthBar(GameObject):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(pygame.Color("red"))
        self.solid = False

    def render(self):
        game.screen.blit(self.image, self.rect)


class GameWorld:

    def __init__(self):
        self.blocks = []
        self.entities = []
        self.gui_items = []

    def add_block(self, obj):
        self.blocks.append(obj)

    def remove_block(self, obj):
        self.blocks.remove(obj)

    def add_entity(self, obj):
        self.entities.append(obj)

    def remove_entity(self, obj):
        self.entities.remove(obj)

    def add_gui(self, obj):
        self.gui_items.append(obj)

    def remove_gui(self, obj):
        self.gui_items.remove(obj)

    def render(self):
        for game_object in self.blocks:
            if game_object.visible:
                game_object.render()
        for game_entity in self.entities:
            if game_entity.visible:
                game_entity.render()
        for gui_item in self.gui_items:
            if gui_item.visible:
                gui_item.render()


world = GameWorld()


class EventBase:

    def __init__(self, name):
        self.name = name
        self.listeners = []

    def __call__(self, *args, **kwargs):
        return self

    def notify_listeners(self):
        for listener in self.listeners:
            listener.notify(self)

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


class RandomNumberEvent(EventBase):

    def __init__(self):
        super().__init__("random_number")
        self.number = random.randint(0, 99)

    def __call__(self, *args, **kwargs):
        self.number = random.randint(0, 99)
        return self


class KeyboardEvent(EventBase):

    def __init__(self):
        super().__init__("keyboard_event")
        self.keyboard_dict = dict()

    def add_key(self, state, char_ord):
        self.keyboard_dict[char_ord] = state

    def update(self):
        for item, key in self.keyboard_dict.items():
            self.keyboard_dict[item] = None


TickEvent = TickEvent()
LMBClickEvent = LMBClickEvent()
RandomNumberEvent = RandomNumberEvent()
KeyboardEvent = KeyboardEvent()


class EventManager:

    def __init__(self):
        self.event_queue = []

    def process_normal(self):
        self.event_queue.append(TickEvent())
        self.event_queue.append(RandomNumberEvent())
        self.event_queue.append(KeyboardEvent())

    def process_pygame(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            KeyboardEvent.add_key(True, event.key)
        elif event.type == pygame.KEYUP:
            KeyboardEvent.add_key(False, event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.event_queue.append(LMBClickEvent(*event.pos))

    def process(self):
        for event in self.event_queue:
            event.notify_listeners()
        self.event_queue.clear()


EventManager = EventManager()


class Engine:

    def __init__(self):
        self.is_running = True
        self.world = world
        self.player = Player(50, 50, 40, 40)
        self.world.add_entity(self.player)
        self.camera = camera

    def run(self):
        while self.is_running:
            game.screen.fill(pygame.Color("black"))
            EventManager.process_normal()
            for event in pygame.event.get():
                EventManager.process_pygame(event)
            EventManager.process()
            self.player.physic()
            self.camera.update(self.player)
            self.world.render()
            pygame.display.update()
            game.fps_clock.tick(game.fps)


#########
#########
# borders
world.add_block(Block(0, 0, 2000, 20))
world.add_block(Block(0, 0, 20, 1000))
world.add_block(Block(0, 980, 2000, 20))
world.add_block(Block(1980, 0, 20, 1000))
# platforms
world.add_block(Block(1000, 700, 600, 40))
world.add_block(Block(400, 200, 500, 40))
world.add_block(Block(1100, 300, 400, 40))
world.add_block(Block(1500, 500, 300, 40))
world.add_block(Block(400, 500, 300, 40))
world.add_block(Block(600, 800, 200, 40))
world.add_block(Block(1700, 200, 200, 40))
# health bar
world.add_gui(HealthBar(50, 50, 100, 30))
#########
#########
engine = Engine()
engine.run()
