from assets import load as use_assets
from filters import recolor, outline
from text import render as render_text
from lib.lerp import lerp
from sprite import Sprite
import config
import pygame
from palette import WHITE, BLACK

class DamageNumber:
  INITIAL_VELOCITY = -2
  GRAVITY = 0.2
  DURATION = 120
  PINCH_DURATION = 7
  BLINK_DURATION = DURATION - PINCH_DURATION
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
    sprite = recolor(sprite, number.color or WHITE)
    sprite = outline(sprite, BLACK)
    return sprite

class DamageValue:
  def __init__(value, number, cell, color=None):
    value.cell = cell
    value.done = False
    value.width = 0
    value.time = 0
    value.numbers = []
    for i, char in enumerate(str(number)):
      number = DamageNumber(value=char, x=i, color=color)
      value.numbers.append(number)
      value.width += number.sprite.get_width()

  def render(value):
    sprites = []
    col, row = value.cell
    x = (col + 0.5) * config.TILE_SIZE - value.width // 2
    y = row * config.TILE_SIZE - 8
    value.time += 1
    for i, number in enumerate(value.numbers):
      number.update()
      image = number.sprite
      number_width = image.get_width()
      number_height = image.get_height()
      if number.time >= DamageNumber.BLINK_DURATION:
        t = (number.time - DamageNumber.BLINK_DURATION) / DamageNumber.PINCH_DURATION
        image = pygame.transform.scale(image, (
          int(number_width * lerp(1, 0, t)),
          int(number_height * lerp(1, 3, t))
        ))
      if number.time >= 0 and (value.time < 60 or value.time % 2):
        number_x = x + number_width // 2 - image.get_width() // 2
        number_y = y + number.y + number_height // 2 - image.get_height() // 2
        sprites.append(Sprite(
          image=image,
          pos=(number_x, number_y),
          layer="numbers"
        ))
      x += number_width - 2
      if number.done and i == len(value.numbers) - 1:
        value.done = True
    return sprites
