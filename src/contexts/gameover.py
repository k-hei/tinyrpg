from math import sin, pi
from random import randrange, randint
import pygame
from pygame import Surface, Rect, SRCALPHA
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from contexts import Context
from contexts.load import LoadContext
from sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE
from colors.palette import BLACK, WHITE
from filters import recolor, outline
from assets import load as use_assets
from anims import Anim
from anims.sine import SineAnim
from anims.flicker import FlickerAnim
from anims.tween import TweenAnim
from easing.expo import ease_out
from transits.dissolve import DissolveOut
import assets

OPTIONS_SPACING = 20
OPTIONS_X = WINDOW_WIDTH // 2 - 32
OPTIONS_Y = WINDOW_HEIGHT // 2 + 16

class TitleCharEnterAnim(TweenAnim): blocking = True
class ChooseAnim(FlickerAnim): blocking = True
class ScrollAnim(Anim):
  speed = 2
  offset = 48
  blocking = True

def get_title_char_offset(a, b):
  if a == "g" and b == "a": return -7
  if a == "m" and b == "e1": return 1
  if b == " ": return 21
  if a == "o" and b == "v": return 1
  if a == "e2" and b == "r": return -12
  return 0

class Hand:
  def __init__(hand, x, y=0):
    hand.x = x
    hand.y = WINDOW_HEIGHT + randrange(48) + y
    hand.darkened = y != 0
    hand.flipped = not randint(0, 1)
    hand.shake_period = randint(2, 4)
    hand.twitch_period = randint(4, 16)
    hand.twitch_offset = randrange(8)

class GameOverContext(Context):
  TITLE_SEQUENCE = ["g", "a", "m", "e1", " ", "o", "v", "e2", "r"]
  choices = [
    "Continue",
    "Load Game"
  ]

  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.choice_index = 0
    ctx.chosen = False
    ctx.anims = [
      SineAnim(target="hand", period=30, amplitude=2),
      ScrollAnim(),
    ]
    ctx.cache_bg = None
    ctx.hands = []
    ctx.title_active = False

  def enter(ctx):
    x = -32
    while x < WINDOW_WIDTH + 32:
      x += randrange(32, 64)
      ctx.hands.append(Hand(x=x, y=-16))
      x += 1

    x = -32
    while x < WINDOW_WIDTH + 32:
      x += randrange(16, 48)
      ctx.hands.append(Hand(x=x))
      x += 1

  def enter_title(ctx):
    ctx.title_active = True
    offset = 0
    for i, char in enumerate(GameOverContext.TITLE_SEQUENCE):
      if char == " ":
        offset += 1
        continue
      ctx.anims.append(TitleCharEnterAnim(
        target=char,
        duration=15,
        delay=5 * (i - offset),
      ))

  def init(ctx):
    triangle_image = assets.sprites["gameover_tri"]
    offset = triangle_image.get_height()
    ctx.cache_bg = Surface((WINDOW_WIDTH, WINDOW_HEIGHT + offset), SRCALPHA)
    pygame.draw.rect(ctx.cache_bg, BLACK, Rect(
      (0, offset),
      WINDOW_SIZE
    ))
    start_x = -triangle_image.get_width() // 2
    x = start_x
    while x < WINDOW_WIDTH - start_x:
      ctx.cache_bg.blit(triangle_image, (x, 0))
      x += triangle_image.get_width()

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)
    if (keyboard.get_state(button) + gamepad.get_state(button) > 1
    or next((a for a in ctx.anims if a.blocking), None)
    or ctx.chosen):
      return
    if button in (pygame.K_UP, pygame.K_w, gamepad.controls.UP):
      return ctx.handle_move(-1)
    if button in (pygame.K_DOWN, pygame.K_s, gamepad.controls.DOWN):
      return ctx.handle_move(1)
    if button in (pygame.K_RETURN, pygame.K_SPACE, gamepad.controls.confirm):
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
    ctx.chosen = True
    ctx.anims.append(ChooseAnim(target="hand", duration=30, on_end=lambda: (
      choice == "Continue" and (
        game := ctx.get_parent(cls="GameContext"),
        game and game.load() or ctx.close(choice),
        ctx.get_head().transition([DissolveOut()])
      ),
      choice == "Load Game" and ctx.open(LoadContext(), on_close=lambda *data: (
        data and (
          game := ctx.get_parent(cls="GameContext"),
          game and game.load(savedata=data[0]) or ctx.close(choice)
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
    scroll_anim = next((a for a in ctx.anims if type(a) is ScrollAnim), None)
    for hand in ctx.hands:
      hand.y -= ScrollAnim.speed
      if hand.y < -assets.sprites["gameover_hand"][0].get_height():
        ctx.hands.remove(hand)
    if scroll_anim:
      bg_y = WINDOW_HEIGHT + scroll_anim.offset - scroll_anim.time * scroll_anim.speed
      if bg_y < WINDOW_HEIGHT // 3 and not ctx.title_active:
        ctx.enter_title()
      if bg_y < -assets.sprites["gameover_tri"].get_height():
        ctx.anims.remove(scroll_anim)

  def view(ctx):
    sprites = []
    assets = use_assets()

    if ctx.get_head().get_depth() == 1:
      bg_image = Surface(WINDOW_SIZE)
      bg_image.fill((255, 255, 255))
      sprites.append(Sprite(
        image=bg_image,
        layer="ui",
      ))

    scroll_anim = next((a for a in ctx.anims if type(a) is ScrollAnim), None)

    if scroll_anim:
      for hand in ctx.hands:
        hand_image = assets.sprites["gameover_hand"][int((scroll_anim.time + hand.twitch_offset) / hand.twitch_period) % 4 == 0]
        if hand.darkened:
          hand_image = recolor(hand_image, BLACK)
        sprites.append(Sprite(
          image=hand_image,
          pos=(hand.x + int(scroll_anim.time / hand.shake_period) % 2, hand.y),
          origin=("center", "top"),
          flip=(hand.flipped, False),
          layer="ui",
        ))
      bg_y = WINDOW_HEIGHT + scroll_anim.offset - scroll_anim.time * ScrollAnim.speed
      sprites.append(Sprite(
        image=ctx.cache_bg,
        pos=(0, bg_y),
        layer="ui",
      ))
    else:
      sprites.append(Sprite(
        image=ctx.cache_bg,
        pos=(0, -assets.sprites["gameover_tri"].get_height()),
        layer="ui",
      ))

    if ctx.title_active:
      chars_x = WINDOW_WIDTH // 2 - assets.sprites["gameover"].get_width() // 2
      char_x = 0
      char_offset = 0
      for i, char in enumerate(GameOverContext.TITLE_SEQUENCE):
        if char == " ":
          continue
        char_anim = next((a for a in ctx.anims if (
          type(a) is TitleCharEnterAnim
          and a.target == char
        )), None)
        char_image = assets.sprites["gameover_" + char]
        if scroll_anim:
          char_image = outline(char_image, BLACK)
          char_offset = -2
        else:
          char_offset = 0
        char_height = char_image.get_height()
        if char_anim:
          char_height *= ease_out(char_anim.pos)
        sprites.append(Sprite(
          image=char_image,
          pos=(chars_x + char_x + char_offset // 2, WINDOW_HEIGHT // 3),
          size=(char_image.get_width(), char_height),
          origin=("left", "center"),
        layer="ui",
        ))
        char_next = GameOverContext.TITLE_SEQUENCE[i + 1] if i + 1 < len(GameOverContext.TITLE_SEQUENCE) else None
        char_x += char_image.get_width() + char_offset + get_title_char_offset(char, char_next)

    flicker_anim = next((a for a in ctx.anims if type(a) is ChooseAnim), None)
    if scroll_anim or next((a for a in ctx.anims if a.blocking and a is not flicker_anim), None):
      return sprites

    choice_y = OPTIONS_Y
    choice_sprites = []
    for i, choice in enumerate(ctx.choices):
      choice_color = WHITE if not flicker_anim or i == ctx.choice_index and flicker_anim.visible else BLACK
      choice_sprites.append(Sprite(
        image=assets.ttf["english"].render(choice.upper(), color=choice_color),
        pos=(OPTIONS_X, choice_y),
        layer="ui",
      ))
      choice_y += OPTIONS_SPACING
    choice_sprite = choice_sprites[ctx.choice_index]
    choice_x = OPTIONS_X - 4
    bounce_anim = next((a for a in ctx.anims if type(a) is SineAnim), None)
    if not flicker_anim or flicker_anim.visible:
      if not flicker_anim and bounce_anim and not ctx.child:
        choice_x += bounce_anim.pos
      _, choice_y = choice_sprite.pos
      sprites.append(Sprite(
        image=assets.sprites["hand"],
        pos=(choice_x, choice_y + choice_sprite.image.get_height() // 2),
        origin=("right", "center"),
        flip=(True, False),
        layer="ui",
      ))
    sprites += choice_sprites
    return sprites + super().view()
