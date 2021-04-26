import pygame

import keyboard

from contexts import Context
from assets import load as use_assets
from actors.town.knight import Knight

from filters import stroke
import palette

import config

TOWER_X = 224
SPAWN_X = TOWER_X - config.TILE_SIZE // 2
ACTOR_Y = 128

class TownContext(Context):
  def __init__(town, parent):
    super().__init__(parent)
    knight = Knight()
    knight.x = SPAWN_X
    knight.facing = -1
    town.hero = knight
    town.actors = [knight]
    town.area = "outskirts"
    town.areas = ["central", "outskirts"]

  def handle_keydown(town, key):
    if town.parent.transits:
      return
    if key == pygame.K_LEFT or key == pygame.K_a:
      town.handle_move(-1)
    elif key == pygame.K_RIGHT or key == pygame.K_d:
      town.handle_move(1)

  def handle_keyup(town, key):
    if key == pygame.K_LEFT or key == pygame.K_a:
      town.handle_movestop()
    elif key == pygame.K_RIGHT or key == pygame.K_d:
      town.handle_movestop()

  def handle_move(town, delta):
    hero = town.hero
    hero.move(delta)
    if hero.x > TOWER_X + config.TILE_SIZE // 2:
      town.parent.dissolve(on_clear=town.parent.goto_dungeon)

  def handle_movestop(town):
    hero = town.hero
    hero.stop_move()

  def draw(town, surface):
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    surface.blit(sprite_bg, (0, 0))
    for actor in town.actors:
      sprite = actor.render()
      sprite = stroke(sprite, palette.WHITE)
      surface.blit(sprite, (actor.x - config.TILE_SIZE // 2, ACTOR_Y - 1))
    surface.blit(sprite_tower, (TOWER_X, ACTOR_Y - 16))
