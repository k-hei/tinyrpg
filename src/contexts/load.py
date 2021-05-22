from dataclasses import dataclass
from math import sin, pi
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip, scale
from contexts import Context
from contexts.prompt import PromptContext, Choice
from contexts.dialogue import DialogueContext
from comps.bg import Bg
from comps.banner import Banner
from comps.log import Log
from config import WINDOW_SIZE
from assets import load as use_assets
from palette import BLACK, WHITE, GOLD, BLUE, YELLOW
from filters import recolor, replace_color, darken, outline, shadow_lite as shadow
from text import render as render_text
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
import savedata
import keyboard

def view_time(secs):
  mins = secs // 60
  secs = secs % 60
  hours = mins // 60
  mins = mins % 60
  hours = "0{}".format(hours) if hours < 10 else str(hours)
  mins = "0{}".format(mins) if mins < 10 else str(mins)
  secs = "0{}".format(secs) if secs < 10 else str(secs)
  return "{}:{}:{}".format(hours, mins, secs)

def get_char_spacing(old_char, new_char):
  if old_char == " ": return -10
  if old_char == "A" and new_char == "T": return -7
  if old_char == "T" and new_char == "A": return -6
  return -4

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class TitleEnterAnim(TweenAnim): pass

class Slot:
  ICON_X = 12
  ICON_Y = 10
  ICON_SPACING = 5
  INFO_X = 104
  GOLD_Y = 12
  TIME_Y = 30
  TEXT_X = 4
  TEXT_Y = 5
  LABEL_X = ICON_X
  LABEL_OVERLAP = 3

  def __init__(slot, number, data=None):
    slot.number = number
    slot.data = data
    slot.anim = None
    slot.cache_tag = None
    slot.cache_surface = None

  def init(slot):
    assets = use_assets()

    tag_image = render_text("FILE {}".format(slot.number), assets.fonts["smallcaps"])
    tag_image = recolor(tag_image, YELLOW)
    tag_image = outline(tag_image, BLACK)
    tag_image = shadow(tag_image, BLACK)
    slot.cache_tag = tag_image

    slot_image = assets.sprites["slot"]
    slot_width = slot_image.get_width()
    slot_height = slot_image.get_height() + tag_image.get_height() - slot.LABEL_OVERLAP

    slot.cache_surface = Surface((slot_width, slot_height), SRCALPHA)
    slot.surface = slot.cache_surface.copy()
    surface = slot.cache_surface
    surface.blit(slot_image, (0, slot.LABEL_OVERLAP))
    surface.blit(tag_image, (slot.LABEL_X, 0))
    if slot.data is None:
      text_image = assets.ttf["roman"].render("[ No data ]")
      text_x = surface.get_width() // 2 - text_image.get_width() // 2
      text_y = (surface.get_height() - slot.LABEL_OVERLAP) // 2 - text_image.get_height() // 2 + slot.LABEL_OVERLAP
      surface.blit(text_image, (text_x, text_y))
    else:
      knight_image = assets.sprites["circ16_knight"]
      mage_image = assets.sprites["circ16_mage"]
      surface.blit(knight_image, (slot.ICON_X, slot.ICON_Y + slot.LABEL_OVERLAP))
      if "mage" in slot.data.chars:
        if "mage" not in slot.data.party:
          mage_image = darken(mage_image)
        surface.blit(mage_image, (slot.ICON_X + knight_image.get_width() + slot.ICON_SPACING, slot.ICON_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["english"].render("Dungeon 2F"), (slot.ICON_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      gold_image = assets.sprites["item_gold"].copy()
      gold_image = replace_color(gold_image, BLACK, GOLD)
      surface.blit(gold_image, (slot.INFO_X, slot.GOLD_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["roman"].render("{}G".format(slot.data.gold)), (slot.INFO_X + 16 + slot.TEXT_X, slot.GOLD_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      time_image = assets.sprites["icon_clock"].copy()
      time_image = replace_color(time_image, BLACK, BLUE)
      surface.blit(time_image, (slot.INFO_X, slot.TIME_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["roman"].render(view_time(slot.data.time)), (slot.INFO_X + 16 + slot.TEXT_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))

  def enter(slot):
    slot.anim = TweenAnim(
      duration=10,
      delay=(slot.number - 1) * 5 + 5
    )

  def update(slot):
    anim = slot.anim
    if anim:
      if anim.done:
        slot.anim = None
      anim.update()

  def render(slot):
    assets = use_assets()
    if slot.anim:
      t = slot.anim.pos
      t = ease_out(t)
      slot_image = assets.sprites["slot"]
      height = slot_image.get_height() * t
      y = slot.LABEL_OVERLAP + slot_image.get_height() // 2 - height // 2
      slot_image = scale(slot_image, (slot_image.get_width(), int(height)))
      slot.surface.fill(0)
      slot.surface.blit(slot_image, (0, y))
      return slot.surface
    else:
      return slot.cache_surface

class LoadContext(Context):
  TITLE = "Load Data".upper()
  SLOT_Y = 52
  SLOT_SPACING = 8 - Slot.LABEL_OVERLAP
  HAND_X = 8
  HAND_Y = 16
  HAND_PERIOD = 30
  HAND_AMP = 2

  def __init__(ctx, on_close=None):
    super().__init__(on_close=on_close)
    ctx.index = 0
    ctx.slots = [
      Slot(1, savedata.load("src/data0.json")),
      Slot(2, savedata.load("src/data1.json"))
    ]
    ctx.hand_y = None
    ctx.bg = Bg(WINDOW_SIZE)
    ctx.banner = Banner(a="Load", y="Delete")
    ctx.cache_surface = None
    ctx.cache_chars = {}
    ctx.anims = []
    ctx.time = 0

  def init(ctx):
    ctx.bg.init()
    ctx.banner.init()
    for slot in ctx.slots:
      slot.init()
      slot.enter()
    ctx.cache_surface = Surface(WINDOW_SIZE)
    assets = use_assets()
    for char in ctx.TITLE:
      if char not in ctx.cache_chars:
        char_image = assets.ttf["roman_large"].render(char)
        char_image = outline(char_image, BLUE)
        char_image = shadow(char_image, BLUE)
        char_image = outline(char_image, WHITE)
        ctx.cache_chars[char] = char_image

  def enter(ctx):
    ctx.anims.append(EnterAnim(duration=20, target=ctx))
    ctx.anims.append(EnterAnim(duration=20, target="TitleBg"))
    for i, char in enumerate(ctx.TITLE):
      ctx.anims.append(TitleEnterAnim(
        duration=7,
        delay=i * 2,
        target=i
      ))
    for i, slot in enumerate(ctx.slots):
      ctx.anims.append(EnterAnim(
        duration=30,
        delay=i * 7,
        target=slot
      ))

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = ctx.index + delta
    if new_index >= 0 and new_index < len(ctx.slots):
      ctx.index = new_index
      return True
    else:
      return False

  def handle_load(ctx):
    savedata = ctx.slots[ctx.index].data
    if savedata is None:
      return False
    ctx.open(PromptContext("Load this file?", [
      Choice("Yes"),
      Choice("No", closing=True)
    ], on_close=lambda choice:
      choice.text == "Yes" and ctx.open(DialogueContext(
        lite=True,
        script=["Save data loaded successfully."],
        on_close=lambda: ctx.get_root().dissolve(on_clear=lambda: ctx.close(savedata))
      ))
    ))

  def handle_delete(ctx):
    if ctx.slots[ctx.index].data is None:
      return False
    ctx.open(PromptContext("Are you sure you would like to delete this file?", [
      Choice("Yes"),
      Choice("No", default=True, closing=True)
    ]))

  def handle_keydown(ctx, key):
    if ctx.anims:
      return False

    if ctx.child:
      return ctx.child.handle_keydown(key)

    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_UP:
      return ctx.handle_move(-1)
    if key == pygame.K_DOWN:
      return ctx.handle_move(1)
    if key in (pygame.K_RETURN, pygame.K_SPACE):
      return ctx.handle_load()
    if key == pygame.K_BACKSPACE:
      return ctx.handle_delete()

  def update(ctx):
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      anim.update()
      if anim.target is ctx:
        break
    else:
      for slot in ctx.slots:
        slot.update()
    ctx.time += 1

  def draw(ctx, surface):
    assets = use_assets()
    surface_clip = ctx.cache_surface
    surface_clip.fill(0)
    ctx.bg.draw(surface_clip)
    slot_image = assets.sprites["slot"]
    slot_x = surface.get_width() // 2 - slot_image.get_width() // 2
    slot_y = ctx.SLOT_Y

    for i, slot in enumerate(ctx.slots):
      slot_image = slot.cache_surface
      slot_anim = next((a for a in ctx.anims if a.target is slot), None)
      from_x = -slot_image.get_width()
      to_x = slot_x
      if slot_anim:
        t = slot_anim.pos
        t = ease_out(t)
        x = lerp(from_x, to_x, t)
      else:
        x = to_x
      if i != ctx.index:
        slot_image = darken(slot_image)
      surface_clip.blit(slot_image, (x, slot_y))
      slot_y += slot_image.get_height() + ctx.SLOT_SPACING

    titlebg_anim = next((a for a in ctx.anims if a.target == "TitleBg"), None)
    titlebg_width = 168
    if titlebg_anim:
      titlebg_width *= ease_out(titlebg_anim.pos)
    pygame.draw.rect(surface_clip, BLUE, Rect(0, 24, titlebg_width, 16))

    char_anims = [a for a in ctx.anims if type(a) is TitleEnterAnim]
    x = 16
    for i, char in enumerate(ctx.TITLE):
      anim = next((a for a in char_anims if a.target == i), None)
      char_image = ctx.cache_chars[char]
      from_y = -char_image.get_height()
      to_y = 16
      if anim:
        t = ease_out(anim.pos)
        y = lerp(from_y, to_y, t)
      else:
        y = to_y
      surface_clip.blit(char_image, (x, y))
      if i + 1 < len(ctx.TITLE):
        x += char_image.get_width() + get_char_spacing(char, ctx.TITLE[i + 1])

    hand_image = assets.sprites["hand"]
    hand_image = flip(hand_image, True, False)
    hand_x = slot_x - hand_image.get_width() + ctx.HAND_X
    hand_x += sin(ctx.time % ctx.HAND_PERIOD / ctx.HAND_PERIOD * 2 * pi) * ctx.HAND_AMP
    hand_y = ctx.SLOT_Y + ctx.index * (slot_image.get_height() + ctx.SLOT_SPACING) + ctx.HAND_Y
    if ctx.hand_y is None:
      ctx.hand_y = hand_y
    else:
      ctx.hand_y += (hand_y - ctx.hand_y) / 4

    anims = [a for a in ctx.anims if type(a) is not TitleEnterAnim]
    if not anims and ctx.child is None and not ctx.get_root().transits:
      surface_clip.blit(hand_image, (hand_x, ctx.hand_y))
      if not ctx.banner.active:
        ctx.banner.enter()
    elif ctx.banner.active:
      ctx.banner.exit()
    ctx.banner.draw(surface_clip)

    surface_rect = surface.get_rect()
    ctx_anim = next((a for a in ctx.anims if a.target is ctx), None)
    if ctx_anim:
      t = ctx_anim.pos
      if type(ctx_anim) is EnterAnim:
        t = ease_out(t)
      elif type(ctx_anim) is ExitAnim:
        t = 1 - t
      height = surface.get_height() * t
      y = surface.get_height() // 2 - height // 2
      surface_rect = Rect((0, y), (surface.get_width(), height))
    surface.blit(surface_clip, (0, surface_rect.top), area=surface_rect)
    if ctx.child:
      ctx.child.draw(surface)
