from dataclasses import dataclass
from math import sin, pi
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip, scale

import lib.input as input
from lib.sprite import Sprite
from lib.lerp import lerp
from lib.filters import recolor, replace_color, darken_image, outline, shadow_lite as shadow

from contexts import Context
from contexts.prompt import PromptContext, Choice
from comps.bg import Bg
from comps.title import Title
from comps.banner import Banner
import assets
from colors.palette import BLACK, GOLD, BLUE, GOLD
from text import render as render_text
from anims.tween import TweenAnim
from easing.expo import ease_in, ease_out
import savedata
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE

def view_ticks(ticks, ms=False):
  display_ms = ms
  secs = ticks // 1000
  ms = (ticks - secs * 1000) // 10
  mins = secs // 60
  secs = secs % 60
  hours = mins // 60
  mins = mins % 60
  hours = "0{}".format(hours) if hours < 10 else str(hours)
  mins = "0{}".format(mins) if mins < 10 else str(mins)
  secs = "0{}".format(secs) if secs < 10 else str(secs)
  ms = "0{}".format(ms) if ms < 10 else str(ms)
  return (display_ms
    and f"{hours}:{mins}:{secs}.{ms}"
    or f"{hours}:{mins}:{secs}")

def view_time(secs):
  return view_ticks(secs * 1000)

def get_char_spacing(old_char, new_char):
  if old_char == " ": return -10
  if old_char == "A" and new_char == "V": return -7
  if old_char == "A" and new_char == "T": return -7
  if old_char == "T" and new_char == "A": return -6
  return -4

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class TitleAnim(TweenAnim): pass
class TitleEnterAnim(TitleAnim): pass
class TitleExitAnim(TitleAnim): pass
class TitleBgAnim(TweenAnim): pass
class TitleBgEnterAnim(TitleBgAnim): pass
class TitleBgExitAnim(TitleBgAnim): pass

class Slot:
  ICON_X = 12
  ICON_Y = 10
  ICON_SPACING = 5
  INFO_X = 96
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
    slot.redraw()

  def enter(slot, on_end=None):
    slot.anim = EnterAnim(
      duration=10,
      delay=(slot.number - 1) * 5,
      on_end=on_end
    )

  def exit(slot, on_end=None):
    slot.anim = ExitAnim(duration=7, on_end=on_end)

  def redraw(slot):
    tag_image = render_text("FILE {}".format(slot.number), assets.fonts["smallcaps"])
    tag_image = recolor(tag_image, GOLD)
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

    savedata = slot.data
    if savedata is None:
      text_image = assets.ttf["normal"].render("[ No data ]")
      text_x = surface.get_width() // 2 - text_image.get_width() // 2
      text_y = (surface.get_height() - slot.LABEL_OVERLAP) // 2 - text_image.get_height() // 2 + slot.LABEL_OVERLAP
      surface.blit(text_image, (text_x, text_y))
    else:
      knight_image = assets.sprites["circ16_knight"]
      mage_image = assets.sprites["circ16_mage"]
      rogue_image = assets.sprites["circ16_rogue"]
      x = slot.ICON_X
      y = slot.ICON_Y + slot.LABEL_OVERLAP

      if "Knight" in savedata.builds:
        if "Knight" not in savedata.party:
          knight_image = darken_image(knight_image)
        surface.blit(knight_image, (x, y))
        x += knight_image.get_width() + slot.ICON_SPACING

      if "Mage" in savedata.builds:
        if "Mage" not in savedata.party:
          mage_image = darken_image(mage_image)
        surface.blit(mage_image, (x, y))
        x += mage_image.get_width() + slot.ICON_SPACING

      if "Rogue" in savedata.builds:
        if "Rogue" not in savedata.party:
          rogue_image = darken_image(rogue_image)
        surface.blit(rogue_image, (x, y))
        x += rogue_image.get_width() + slot.ICON_SPACING

      place = (savedata.place == "town"
        and "Outskirts"
        or "Dungeon {}F".format(savedata.dungeon.floor_index))
      surface.blit(assets.ttf["english"].render(place), (slot.ICON_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      gold_image = assets.sprites["item_gold"].copy()
      gold_image = replace_color(gold_image, BLACK, GOLD)
      surface.blit(gold_image, (slot.INFO_X, slot.GOLD_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["normal"].render("{}G".format(savedata.gold)), (slot.INFO_X + 16 + slot.TEXT_X, slot.GOLD_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))
      time_image = assets.sprites["icon_clock"].copy()
      time_image = replace_color(time_image, BLACK, BLUE)
      surface.blit(time_image, (slot.INFO_X, slot.TIME_Y + slot.LABEL_OVERLAP))
      surface.blit(assets.ttf["normal"].render(view_time(savedata.time)), (slot.INFO_X + 16 + slot.TEXT_X, slot.TIME_Y + slot.TEXT_Y + slot.LABEL_OVERLAP))

  def reload(slot):
    slot.exit(on_end=lambda: (
      slot.redraw(),
      slot.enter()
    ))

  def save(slot, data):
    slot.data = data
    slot.reload()

  def clear(slot):
    slot.data = None
    slot.reload()

  def update(slot):
    anim = slot.anim
    if anim:
      if anim.done:
        slot.anim = None
      anim.update()

  def render(slot):
    if slot.anim:
      t = slot.anim.pos
      if type(slot.anim) is EnterAnim:
        t = ease_out(t)
      elif type(slot.anim) is ExitAnim:
        t = 1 - t
      slot_image = assets.sprites["slot"]
      height = slot_image.get_height() * t
      y = slot.LABEL_OVERLAP + slot_image.get_height() // 2 - height // 2
      slot_image = scale(slot_image, (slot_image.get_width(), int(height)))
      slot.surface.fill(0)
      slot.surface.blit(slot_image, (0, y))
      return slot.surface
    else:
      return slot.cache_surface

class DataContext(Context):
  SLOT_Y = 52
  SLOT_SPACING = 8 - Slot.LABEL_OVERLAP
  HAND_X = 8
  HAND_Y = 16
  HAND_PERIOD = 30
  HAND_AMP = 2
  EXTRA_CONTROLS = {}
  TITLE = "MANAGE DATA"
  ACTION = ""

  def __init__(ctx, on_close=None):
    super().__init__(on_close=on_close)
    ctx.index = 0
    ctx.slots = [
      Slot(1, savedata.load("src/data00.json")),
      Slot(2, savedata.load("src/data01.json"))
    ]
    ctx.hand_y = None
    ctx.bg = None
    ctx.title = None
    ctx.banner = None
    ctx.cache_surface = None
    ctx.cache_chars = {}
    ctx.anims = []
    ctx.comps = []
    ctx.time = 0
    ctx.can_close = True
    ctx.hidden = False
    ctx.exiting = False

  def init_view(ctx):
    ctx.bg = Bg(WINDOW_SIZE)
    ctx.bg.init()
    ctx.title = Title(text=ctx.TITLE)
    ctx.title.enter()
    ctx.banner = Banner(**ctx.EXTRA_CONTROLS, a=ctx.ACTION, y="Delete")
    ctx.banner.init()
    for slot in ctx.slots:
      slot.init()
      slot.enter()
    ctx.comps = [ctx.title]
    ctx.cache_surface = Surface(WINDOW_SIZE)

  def enter(ctx):
    ctx.exiting = False
    ctx.anims.append(EnterAnim(duration=20, target=ctx))
    ctx.enter_slots()

  def enter_slots(ctx):
    for i, slot in enumerate(ctx.slots):
      ctx.anims.append(EnterAnim(
        duration=30,
        delay=i * 7,
        target=slot
      ))

  def exit_slots(ctx):
    for i, slot in enumerate(ctx.slots):
      ctx.anims.append(ExitAnim(
        duration=15,
        delay=i * 7,
        target=slot
      ))

  def exit(ctx):
    ctx.exiting = True
    ctx.anims.append(ExitAnim(
      duration=10,
      target=ctx,
      on_end=ctx.close
    ))

  def hide(ctx, on_end=None):
    ctx.hidden = True
    ctx.title.exit()
    ctx.exit_slots()
    ctx.anims[-1].on_end = on_end

  def show(ctx, on_end=False):
    ctx.hidden = False
    ctx.title.enter()
    ctx.enter_slots()

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = ctx.index + delta
    if new_index >= 0 and new_index < len(ctx.slots):
      ctx.index = new_index
      return True
    else:
      return False

  def handle_action(ctx):
    pass

  def handle_delete(ctx):
    slot = ctx.slots[ctx.index]
    if slot.data is None:
      return False
    ctx.open(PromptContext("Are you sure you would like to delete this file?", [
      Choice("Yes"),
      Choice("No", default=True, closing=True)
    ]), on_close=lambda choice: (
      choice and choice.text == "Yes" and ctx.delete_data(slot)
    ))

  def delete_data(ctx, slot):
    slot.clear()
    savedata.delete("src/data0{}.json".format(ctx.index))

  def handle_close(ctx):
    if not ctx.can_close:
      return None
    ctx.open(PromptContext("Return to the game?", [
      Choice("Yes", closing=True),
      Choice("No", default=True, closing=True)
    ]), on_close=lambda choice: (
      choice and choice.text == "Yes" and ctx.exit()
    ))

  def handle_press(ctx, button):
    if ctx.anims or ctx.exiting or next((c for c in ctx.comps if c.anims), None) or ctx.get_head().transits:
      return False

    if ctx.child:
      return ctx.child.handle_press(button)

    if input.get_state(button) > 1:
      return

    controls = input.resolve_controls(button)
    button = input.resolve_button(button)

    if button == input.BUTTON_UP:
      return ctx.handle_move(-1)

    if button == input.BUTTON_DOWN:
      return ctx.handle_move(1)

    if input.CONTROL_CONFIRM in controls:
      return ctx.handle_action()

    if input.CONTROL_MANAGE in controls:
      return ctx.handle_delete()

    if input.CONTROL_CANCEL in controls or input.CONTROL_PAUSE in controls:
      return ctx.handle_close()

  def update(ctx):
    super().update()

    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      anim.update()
      if anim.target is ctx:
        break
    else:
      for slot in ctx.slots:
        slot.update()

    for comp in ctx.comps:
      comp.update()

    ctx.time += 1

  def view(ctx):
    if not ctx.bg:
      ctx.init_view()

    sprites = []
    surface_clip = ctx.cache_surface
    surface_clip.fill(0)
    ctx.bg.draw(surface_clip)
    slot_image = assets.sprites["slot"]
    slot_x = WINDOW_WIDTH // 2 - slot_image.get_width() // 2
    slot_y = ctx.SLOT_Y

    for i, slot in enumerate(ctx.slots):
      slot_image = slot.render()
      slot_anim = next((a for a in ctx.anims if a.target is slot), None)
      from_x = -slot_image.get_width()
      to_x = slot_x
      if type(slot_anim) is EnterAnim:
        t = slot_anim.pos
        t = ease_out(t)
        x = lerp(from_x, to_x, t)
      elif type(slot_anim) is ExitAnim:
        t = slot_anim.pos
        t = ease_in(t)
        x = lerp(to_x, from_x, t)
      elif not ctx.hidden:
        x = to_x
      else:
        x = None

      if x is not None:
        if i != ctx.index:
          slot_image = darken_image(slot_image)
        surface_clip.blit(slot_image, (x, slot_y))

      slot_y += slot_image.get_height() + ctx.SLOT_SPACING

    sprites += ctx.title.view()

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
    if not anims and ctx.child is None and not ctx.get_head().transits:
      surface_clip.blit(hand_image, (hand_x, ctx.hand_y))
      if not ctx.banner.active:
        ctx.banner.enter()
    elif ctx.banner.active:
      ctx.banner.exit()
    ctx.banner.draw(surface_clip)

    surface_rect = Rect((0, 0), WINDOW_SIZE)
    ctx_anim = next((a for a in ctx.anims if a.target is ctx), None)
    if ctx_anim:
      t = ctx_anim.pos
      if type(ctx_anim) is EnterAnim:
        t = ease_out(t)
      elif type(ctx_anim) is ExitAnim:
        t = 1 - t
      height = WINDOW_HEIGHT * t
      y = WINDOW_HEIGHT // 2 - height // 2
      surface_rect = Rect((0, y), (WINDOW_WIDTH, height))

    sprites.insert(0, Sprite(
      image=surface_clip,
      pos=(0, surface_rect.top),
      size=surface_rect.size,
    ))

    for sprite in sprites:
      sprite.layer = "ui"

    return sprites + super().view()
