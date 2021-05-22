from math import sin, pi
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
from contexts import Context
from contexts.prompt import PromptContext, Choice
from comps.bg import Bg
from comps.banner import Banner
from config import WINDOW_SIZE
from assets import load as use_assets
from palette import BLACK, WHITE, GOLD, BLUE, YELLOW
from filters import recolor, replace_color, darken, outline, shadow_lite as shadow
from text import render as render_text
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

  def render(slot):
    assets = use_assets()
    text_image = render_text("FILE {}".format(slot.number), assets.fonts["smallcaps"])
    text_image = recolor(text_image, YELLOW)
    text_image = outline(text_image, BLACK)
    text_image = shadow(text_image, BLACK)
    slot_image = assets.sprites["slot"]
    slot_width = slot_image.get_width()
    slot_height = slot_image.get_height() + text_image.get_height() - slot.LABEL_OVERLAP
    surface = Surface((slot_width, slot_height), SRCALPHA)
    surface.blit(slot_image, (0, slot.LABEL_OVERLAP))
    surface.blit(text_image, (slot.LABEL_X, 0))
    if slot.data is None:
      text_image = assets.ttf["roman"].render("[ No data ]")
      text_x = surface.get_width() // 2 - text_image.get_width() // 2
      text_y = (surface.get_height() - slot.LABEL_OVERLAP) // 2 - text_image.get_height() // 2 + slot.LABEL_OVERLAP
      surface.blit(text_image, (text_x, text_y))
    else:
      surface.blit(assets.sprites["circ16_knight"], (slot.ICON_X, slot.ICON_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.sprites["circ16_mage"], (slot.ICON_X + assets.sprites["circ16_knight"].get_width() + slot.ICON_SPACING, slot.ICON_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["english"].render("Dungeon 2F"), (slot.ICON_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      gold_image = assets.sprites["item_gold"].copy()
      gold_image = replace_color(gold_image, BLACK, GOLD)
      surface.blit(gold_image, (slot.INFO_X, slot.GOLD_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["roman"].render("{}G".format(slot.data.gold)), (slot.INFO_X + 16 + slot.TEXT_X, slot.GOLD_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      time_image = assets.sprites["icon_clock"].copy()
      time_image = replace_color(time_image, BLACK, BLUE)
      surface.blit(time_image, (slot.INFO_X, slot.TIME_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["roman"].render(view_time(slot.data.time)), (slot.INFO_X + 16 + slot.TEXT_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
    return surface

class LoadContext(Context):
  SLOT_Y = 52
  SLOT_SPACING = 8 - Slot.LABEL_OVERLAP
  HAND_X = 8
  HAND_Y = 16
  HAND_PERIOD = 30
  HAND_AMP = 2

  def __init__(ctx):
    super().__init__()
    ctx.index = 0
    ctx.slots = [
      Slot(1, savedata.load("src/data0.json")),
      Slot(2, savedata.load("src/data1.json"))
    ]
    ctx.hand_y = None
    ctx.bg = Bg(WINDOW_SIZE)
    ctx.banner = Banner(a="Load", y="Delete")
    ctx.draws = 0

  def init(ctx):
    ctx.bg.init()
    ctx.banner.init()

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = ctx.index + delta
    if new_index >= 0 and new_index < len(ctx.slots):
      ctx.index = new_index
      return True
    else:
      return False

  def handle_load(ctx):
    if ctx.slots[ctx.index].data is None:
      return False
    ctx.open(PromptContext("Load this file?", [
      Choice("Yes"),
      Choice("No", closing=True)
    ]))

  def handle_delete(ctx):
    if ctx.slots[ctx.index].data is None:
      return False
    ctx.open(PromptContext("Are you sure you would like to delete this file?", [
      Choice("Yes"),
      Choice("No", default=True, closing=True)
    ]))

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
      return ctx.handle_load()
    if key == pygame.K_BACKSPACE:
      return ctx.handle_delete()

  def draw(ctx, surface):
    ctx.bg.draw(surface)
    ctx.banner.draw(surface)

    assets = use_assets()

    slot_image = assets.sprites["slot"]
    slot_x = surface.get_width() // 2 - slot_image.get_width() // 2
    slot_y = ctx.SLOT_Y

    for i, slot in enumerate(ctx.slots):
      slot_image = Slot.render(slot)
      if i != ctx.index:
        slot_image = darken(slot_image)
      surface.blit(slot_image, (slot_x, slot_y))
      slot_y += slot_image.get_height() + ctx.SLOT_SPACING

    pygame.draw.rect(surface, BLUE, Rect(0, 24, 160, 16))
    load_image = assets.ttf["roman_large"].render("LOAD")
    data_image = assets.ttf["roman_large"].render("DATA")
    space_width = 8
    title_width = load_image.get_width() + space_width + data_image.get_width()
    title_height = load_image.get_height()
    title_image = Surface((title_width, title_height), SRCALPHA)
    title_image.blit(load_image, (0, 0))
    title_image.blit(data_image, (load_image.get_width() + space_width, 0))
    title_image = outline(title_image, BLUE)
    title_image = shadow(title_image, BLUE)
    title_image = outline(title_image, WHITE)
    surface.blit(title_image, (16, 16))

    hand_image = assets.sprites["hand"]
    hand_image = flip(hand_image, True, False)
    hand_x = slot_x - hand_image.get_width() + ctx.HAND_X
    hand_x += sin(ctx.draws % ctx.HAND_PERIOD / ctx.HAND_PERIOD * 2 * pi) * ctx.HAND_AMP
    hand_y = ctx.SLOT_Y + ctx.index * (slot_image.get_height() + ctx.SLOT_SPACING) + ctx.HAND_Y
    if ctx.hand_y is None:
      ctx.hand_y = hand_y
    else:
      ctx.hand_y += (hand_y - ctx.hand_y) / 4
    if ctx.child is None:
      surface.blit(hand_image, (hand_x, ctx.hand_y))

    if ctx.child:
      ctx.child.draw(surface)

    ctx.draws += 1
