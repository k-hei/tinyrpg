from math import sin, pi
import pygame
from pygame import Surface
import keyboard
from contexts import Context
from contexts.load import LoadContext
from sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE
from colors.palette import BLACK
from assets import load as use_assets
from anims.sine import SineAnim
from anims.flicker import FlickerAnim
from transits.dissolve import DissolveOut

OPTIONS_SPACING = 20
OPTIONS_X = WINDOW_WIDTH // 2 - 32
OPTIONS_Y = WINDOW_HEIGHT // 2 + 16

class ChooseAnim(FlickerAnim): blocking = True

class GameOverContext(Context):
  choices = [
    "Continue",
    "Load Game"
  ]

  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.choice_index = 0
    ctx.anims = [SineAnim(target="hand", period=30, amplitude=2)]
    ctx.cache_bg = None

  def init(ctx):
    ctx.cache_bg = Surface(WINDOW_SIZE)
    ctx.cache_bg.fill(BLACK)

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if keyboard.get_pressed(key) > 1:
      return
    if key == pygame.K_UP:
      return ctx.handle_move(-1)
    if key == pygame.K_DOWN:
      return ctx.handle_move(1)
    if key in (pygame.K_RETURN, pygame.K_SPACE):
      return ctx.handle_choose()

  def handle_move(ctx, delta):
    old_index = ctx.choice_index
    new_index = old_index + delta
    if new_index < 0:
      new_index = 0
      return False
    elif new_index > len(ctx.choices) - 1:
      new_index = len(ctx.choices) - 1
      return False
    ctx.choice_index = new_index
    return True

  def handle_choose(ctx):
    choice = ctx.choices[ctx.choice_index]
    ctx.anims.append(ChooseAnim(target="hand", duration=30, on_end=lambda: (
      choice == "Continue" and (
        game := ctx.get_parent(cls="GameContext"),
        game and game.load(),
        game.get_head().transition([DissolveOut()])
      ),
      choice == "Load Game" and ctx.open(LoadContext(), on_close=lambda *data: (
        data and (
          game := ctx.get_parent(cls="GameContext"),
          game and game.load(savedata=data[0])
        )
      ))
    )))
    return True

  def update(ctx):
    super().update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def view(ctx):
    sprites = []
    assets = use_assets()
    sprites.append(Sprite(
      image=ctx.cache_bg,
    ))
    sprites.append(Sprite(
      image=assets.sprites["game_over"],
      pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3),
      origin=("center", "center"),
    ))
    choice_y = OPTIONS_Y
    choice_sprites = []
    for choice in ctx.choices:
      choice_sprites.append(Sprite(
        image=assets.ttf["english"].render(choice.upper()),
        pos=(OPTIONS_X, choice_y),
      ))
      choice_y += OPTIONS_SPACING
    choice_sprite = choice_sprites[ctx.choice_index]
    choice_x = OPTIONS_X - 4
    bounce_anim = next((a for a in ctx.anims if type(a) is SineAnim), None)
    flicker_anim = next((a for a in ctx.anims if type(a) is ChooseAnim), None)
    if not flicker_anim or flicker_anim.visible:
      if not flicker_anim and bounce_anim and not ctx.child:
        choice_x += bounce_anim.pos
      _, choice_y = choice_sprite.pos
      sprites.append(Sprite(
        image=assets.sprites["hand"],
        pos=(choice_x, choice_y + choice_sprite.image.get_height() // 2),
        origin=("right", "center"),
        flip=(True, False),
      ))
    sprites += choice_sprites
    return sprites + super().view()
