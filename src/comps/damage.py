from assets import load as use_assets
from filters import recolor, outline
from text import render as render_text
from lib.lerp import lerp
import config
import pygame

class DamageNumber:
  INITIAL_VELOCITY = -2
  GRAVITY = 0.2
  DURATION = 75
  STAGGER = 10
  BOUNCE = 0

  def __init__(number, value, x, color=None):
    number.value = value
    number.x = x
    number.color = color
    number.y = 0
    number.done = False
    number.time = -DamageNumber.STAGGER * x
    number.duration = DamageNumber.DURATION
    number.velocity = DamageNumber.INITIAL_VELOCITY
    number.sprite = number.render()

  def update(number):
    if number.done:
      return
    number.time += 1
    if number.time < 0:
      return
    number.y += number.velocity
    number.velocity += DamageNumber.GRAVITY
    if number.y > 0:
      number.y = 0
      number.velocity *= -DamageNumber.BOUNCE
    if number.time == number.duration:
      number.done = True

  def render(number):
    assets = use_assets()
    font = assets.fonts["smallcaps"]
    sprite = render_text(number.value, font)
    sprite = recolor(sprite, number.color or (0xFF, 0xFF, 0xFF))
    sprite = outline(sprite, (0x00, 0x00, 0x00))
    return sprite

class DamageValue:
  def __init__(value, number, cell, color=None):
    value.cell = cell
    value.done = False
    value.width = 0
    value.time = 0
    value.numbers = []
    for i, char in enumerate(number):
      number = DamageNumber(value=char, x=i, color=color)
      value.numbers.append(number)
      value.width += number.sprite.get_width()

  def draw(value, surface, camera):
    camera_x, camera_y = camera
    col, row = value.cell
    x = (col + 0.5) * config.TILE_SIZE - round(camera_x) - value.width // 2
    y = row * config.TILE_SIZE - round(camera_y) - 8
    value.time += 1
    for i, number in enumerate(value.numbers):
      number.update()
      sprite = number.sprite
      number_width = sprite.get_width()
      number_height = sprite.get_height()
      if number.time >= 68:
        t = (number.time - 68) / 7
        sprite = pygame.transform.scale(sprite, (
          int(number_width * lerp(1, 0, t)),
          int(number_height * lerp(1, 3, t))
        ))
      if number.time >= 0 and (value.time < 60 or value.time % 2):
        surface.blit(sprite, (
          x + number_width // 2 - sprite.get_width() // 2,
          y + number.y + number_height // 2 - sprite.get_height() // 2
        ))
      x += number_width - 2
      if number.done and i == len(value.numbers) - 1:
        value.done = True
